def extract_and_clean_by_xpath(desired_xpath):
    extracted_data = response.xpath(desired_xpath).extract_first()
    try:
        extracted_data = extracted_data.replace('²', '2')
        extracted_data = re.sub(r' {2,}', '', extracted_data)
        extracted_data = re.sub(r'\n', '', extracted_data)
        extracted_data = re.sub(r'\t', '', extracted_data)
        extracted_data = re.sub(r'\r', '', extracted_data)
        # extracted_data = re.sub(r'[^\w|\d|\s]', '', extracted_data)

    except Exception:
        print('Xpath was not found and thus regex cannot operate on it.')
        extracted_data = None
    return extracted_data