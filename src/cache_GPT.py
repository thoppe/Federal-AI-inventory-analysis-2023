from utils import query, embed, recover_list_from_response
from dspipe import Pipe
from wasabi import msg as MSG
from diskcache import Cache
import json
import numpy as np
import itertools


OpenAI_token_cost_per_1K = 0.002
OpenAI_embed_token_cost_per_1K = 0.0004


def flatten_func(nested_list):
    return list(itertools.chain.from_iterable(nested_list))


class ChatGPT:
    def __init__(self, cache, max_tokens, parallel_threads=1, verbose=False):

        if isinstance(cache, str):
            cache = Cache(cache)

        self.cache = cache
        self.max_tokens = max_tokens
        self.parallel_threads = parallel_threads
        self.verbose = verbose

        self.total_tokens = 0
        self.total_API_calls = 0

        self.total_embed_tokens = 0
        self.total_embed_API_calls = 0

    @property
    def total_cost(self):
        return OpenAI_token_cost_per_1K * (self.total_tokens / 1_000)

    @property
    def total_embed_cost(self):
        return OpenAI_embed_token_cost_per_1K * (self.total_embed_tokens / 1_000)

    def return_from_cache(self, messages, output):
        result = self.cache[messages]
        cost = result["usage"]["total_tokens"]

        if output == "raw":
            return result, cost

        result = result["choices"][0]["message"]["content"]

        if output == "list":
            return recover_list_from_response(result), cost

        elif output == "json":
            return json.loads(result), cost

        elif output == "text":
            return result, cost

        else:
            raise ValueError(f"Unknown output {output}")

    def ASK(
        self,
        messages,
        output=None,
        force=False,
    ):

        valid_outputs = ["text", "raw", "json", "list"]
        try:
            assert output in valid_outputs
        except Exception as EX:
            print(f"{EX} Expected output to be one of {valid_outputs} for {output}")
            exit()

        if messages in self.cache and not force:
            return self.return_from_cache(messages, output)

        # max_visible_print = 1_000
        # MSG.warn(messages[-1]["content"][:max_visible_print])

        js = query(messages, max_tokens=self.max_tokens, n=1)
        token_cost = js["usage"]["total_tokens"]
        MSG.info(f"TOKENS USED {token_cost}")

        content = js["choices"][0]["message"]["content"]

        if output == "list":
            try:
                assert len(recover_list_from_response(content)) > 1
            except Exception as EX:
                MSG.fail("FAILED NOT BULLETED", EX)
                print(content)
                return self.ASK(
                    messages,
                    output=output,
                    force=force,
                )

        if output == "json":
            try:
                json.loads(content)
            except Exception as EX:
                MSG.fail("FAILED, BAD JSON", EX)
                print(content)
                return self.ASK(
                    messages,
                    output=output,
                    force=force,
                )

        # Cache the result
        self.cache[messages] = js

        if self.verbose:
            prompt = messages[0]["content"]
            print(f"USR: {prompt}\nGPT: {content}")

        # Return from cache
        return self.return_from_cache(messages, output)

    def invalidate(self, q):
        messages = [{"role": "user", "content": q}]
        if messages in self.cache:
            del self.cache[messages]
            return True
        return False

    def __call__(
        self,
        q,
        force=False,
        output="text",
    ):
        messages = [{"role": "user", "content": q}]
        return self.ASK(
            messages,
            output=output,
            force=force,
        )

    def format_string_from_kwargs(self, string, **kwargs):
        """
        Given a string and kwargs that are {key0:LIST, key1:LIST, ...}
        Return a list of strings with each key replaced for the lists.
        """

        values = [list(kwargs[key]) for key in kwargs]

        # Assert all inputs are the same length
        lst_lengths = list(map(len, values))
        assert all([lst_lengths[0] == x for x in lst_lengths])

        # Format all the strings ahead of time to feed to parallel processing
        string_formats = [
            dict(zip(kwargs, items)) for items in itertools.zip_longest(*values)
        ]
        return [string.format(**f) for f in string_formats]

    def multiInvalidate(self, idx, prompt, **kwargs):
        raise NotImplementedError
        prompts = self.format_string_from_kwargs(prompt, **kwargs)

        for is_valid, p in zip(idx, prompts):
            print(is_valid, p)
        exit()

    def multiASK(self, prompt, output="text", force=False, flatten=False, **kwargs):

        """
        Calls self.__call__ in parallel.
        Output is one of [text, raw, list, json]

        Need to set all inputs through the kwargs.
        """
        prompts = self.format_string_from_kwargs(prompt, **kwargs)

        results = Pipe(prompts)(
            self,
            self.parallel_threads,
            force=force,
            output=output,
        )

        result, costs = zip(*results)
        self.total_tokens += sum(costs)
        self.total_API_calls += len(costs)

        if flatten:
            result = flatten_func(result)

        return result

    def embed(self, text):
        cache_key = f"OPENAI_EMBEDCACHE_{text}"

        if cache_key not in self.cache:
            self.cache[cache_key] = embed(text)

        result = self.cache[cache_key]

        self.total_embed_tokens += result["usage"]["total_tokens"]
        self.total_embed_API_calls += 1

        v = result["data"][0]["embedding"]
        return np.array(v)

        return self.cache[cache_key]["data"][0]["embedding"]

    def __repr__(self):
        return (
            f"Cost   : ${self.total_cost:0.2f}\n"
            f"Tokens : {self.total_tokens:,d}\n"
            f"Calls  : {self.total_API_calls}\n"
            f"ECost  : ${self.total_embed_cost:0.2f}\n"
            f"ETokens: {self.total_embed_tokens:,d}\n"
            f"ECalls : {self.total_embed_API_calls}"
        )
