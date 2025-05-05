import pytest
import core.utils as utils

def test_alpha_converter():
    # Integer to letter
    assert utils.alpha_converter(1) == 'A'
    assert utils.alpha_converter(2) == 'B'
    assert utils.alpha_converter(26) == 'Z'
    assert utils.alpha_converter(27) == 'AA'
    assert utils.alpha_converter(28) == 'AB'
    assert utils.alpha_converter(52) == 'AZ'
    assert utils.alpha_converter(53) == 'BA'
    assert utils.alpha_converter(702) == 'ZZ'
    assert utils.alpha_converter(703) == 'AAA'
    assert utils.alpha_converter(18278) == 'ZZZ'

    # Integer to letter (0-based result)
    assert utils.alpha_converter(0, True) == 'A'
    assert utils.alpha_converter(1, True) == 'B'
    assert utils.alpha_converter(25, True) == 'Z'
    assert utils.alpha_converter(26, True) == 'AA'
    assert utils.alpha_converter(27, True) == 'AB'
    assert utils.alpha_converter(51, True) == 'AZ'
    assert utils.alpha_converter(52, True) == 'BA'
    assert utils.alpha_converter(701, True) == 'ZZ'
    assert utils.alpha_converter(702, True) == 'AAA'
    assert utils.alpha_converter(18277, True) == 'ZZZ'

    # String letters to number
    assert utils.alpha_converter('A') == 1
    assert utils.alpha_converter('B') == 2
    assert utils.alpha_converter('Z') == 26
    assert utils.alpha_converter('AA') == 27
    assert utils.alpha_converter('AZ') == 52
    assert utils.alpha_converter('BA') == 53
    assert utils.alpha_converter('ZZ') == 702
    assert utils.alpha_converter('AAA') == 703

    # String letters to number (0-based result)
    assert utils.alpha_converter('A', True) == 0
    assert utils.alpha_converter('B', True) == 1
    assert utils.alpha_converter('Z', True) == 25
    assert utils.alpha_converter('AA', True) == 26
    assert utils.alpha_converter('AZ', True) == 51
    assert utils.alpha_converter('BA', True) == 52
    assert utils.alpha_converter('ZZ', True) == 701
    assert utils.alpha_converter('AAA', True) == 702

    # String number to letter
    assert utils.alpha_converter('1') == 'A'
    assert utils.alpha_converter('27') == 'AA'

    # Invalid input
    with pytest.raises(ValueError):
        utils.alpha_converter('A1')  # mix of letters and digits

    with pytest.raises(ValueError):
        utils.alpha_converter(0)  # number too small

    with pytest.raises(TypeError):
        utils.alpha_converter(3.14)  # unsupported type