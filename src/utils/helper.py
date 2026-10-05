import json


def parse_json_response(response, default):
	content = getattr(response, "content", response)
	if not isinstance(content, str):
		content = str(content)

	try:
		parsed = json.loads(content)
	except (TypeError, ValueError):
		start = content.find("{")
		end = content.rfind("}")
		if start < 0 or end <= start:
			return dict(default)
		try:
			parsed = json.loads(content[start : end + 1])
		except (TypeError, ValueError):
			return dict(default)

	return parsed if isinstance(parsed, dict) else dict(default)
