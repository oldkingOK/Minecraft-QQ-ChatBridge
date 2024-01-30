def image_url_to_cicode(url, display_name):
	"""
	把图片链接处理成ChatImage Code，便可以在客户端显示图片
	"""
	return f"[[CICode,url={url},name={display_name}]]";