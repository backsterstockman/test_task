import pytest
from src.file import (
    add_args, load_data, check_arguments, apply_where, apply_aggregate
    )

PARSER = add_args()
DATA = load_data('src/data.csv')


@pytest.mark.parametrize(
        "parser",
        [
            (PARSER)
        ]
)
def test_add_args(parser):
    option_strings = {
        opt
        for action in parser._actions
        for opt in action.option_strings
    }

    assert '--file' in option_strings
    assert '--where' in option_strings
    assert '--aggregate' in option_strings


@pytest.mark.parametrize(
        "parser",
        [
            (PARSER)
        ]
)
def test_input_args(parser):
    args = parser.parse_args(
        ['--file', 'foo.csv',
         '--where', 'brand=xiaomi',
         '--aggregate', 'rating=min']
        )

    assert args.file == 'foo.csv'
    assert args.where == 'brand=xiaomi'
    assert args.aggregate == 'rating=min'


@pytest.mark.parametrize(
        "parser, expected_file",
        [
            (PARSER, True),
            (PARSER, False)
        ]
)
def test_check_args(parser, expected_file):
    if expected_file:
        assert check_arguments(parser, ['--file', 'foo.csv']) is True
    else:
        assert check_arguments(parser, []) is False


@pytest.mark.parametrize(
        "path, expected_nonempty",
        [
            ('src/data.csv', True),
            ('src/products.csv', False)
        ]
)
def test_load_data(path, expected_nonempty):
    data = load_data(path)
    if expected_nonempty:
        assert data != []
    else:
        assert data == []


@pytest.mark.parametrize(
        "data, where, expected_correct_where",
        [
            (DATA, 'rating>4.5', True),
            (DATA, '', False),
            (DATA, 'brand>xiaomi', False),
            (DATA, 'brand-xiaomi', False),
            (DATA, 'rating=4.4', True),
            (DATA, 'rating<4.8', True),
            (DATA, 'brand=xiaomi', True),

        ]
)
def test_apply_where(data, where, expected_correct_where):
    filtered = apply_where(data, where)
    if expected_correct_where:
        assert filtered != data
    else:
        assert filtered == data


@pytest.mark.parametrize(
        "data, aggregate, expected_correct_aggregate",
        [
            (DATA, 'rating=min', True),
            (DATA, '', False),
            (DATA, 'rating>min', False),
            (DATA, 'brand=min', False),
            (DATA, 'price=max', True),
            (DATA, 'rating=avg', True),           
        ]
)
def test_apply_aggregate(data, aggregate, expected_correct_aggregate):
    result = apply_aggregate(data, aggregate)
    if expected_correct_aggregate:
        if len(result) == 2:
            assert result != ()
        else:
            assert result == ()
    else:
        assert result == ()
