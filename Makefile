target_url="https://www.ai.gov/ai-use-case-inventories/"
output_md5file="data/ai_gov_md5hash.csv"

streamlit:
	streamlit run streamlit_demo.py 

lint:
	black *.py src

record_website_hash:
	@python src/md5_webpage.py $(target_url) >> $(output_md5file)
