from pycprof import Profile

import ujson as json

apiJson = json.dumps({"allocation":{"id":"69269214106912","pos":"1099884920832","size":"156832","addrsp":"{\"type\":\"uva\"}\n","mem":"pageable","loc":"{\"type\":\"cuda\",\"id\":\"0\"}\n"}})
allocJson = ""

def test_profile():
    jsonStr = "{api: {}}"
    assert True

def test_success():
    assert True