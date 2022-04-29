import pytest

###########################
# ENTITY PROPERTIES 
###########################


@pytest.fixture(scope="module", params=[1, 5, 10, 20])
def radius(request):
    return request.param

