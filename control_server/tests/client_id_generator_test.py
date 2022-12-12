from uuid import UUID

from control_server.src.crypto.client_id_generator import ClientIdGenerator


def test_simple_id_generation():
    generator = ClientIdGenerator(
        id_key='test',
        client_id_keys=['working_id']
    )

    generated_id = generator.generate_from_data(
        {
            'working_id': 'test',
            'non_working_id': 'test'
        }
    )

    assert generated_id is not None
    assert isinstance(generated_id, UUID)


def test_two_ids():
    generator = ClientIdGenerator(
        id_key='test',
        client_id_keys=['working_id']
    )

    datasets = [
        {
            'working_id': 'test',
            'non_working_id': 'test'
        },
        {
            'working_id': 'test',
        }
    ]

    ids = [
        generator.generate_from_data(data) for data in datasets
    ]

    assert all(
        current_id == ids[0] for current_id in ids
    )


def test_two_empty_ids():
    generator = ClientIdGenerator(
        id_key='test',
        client_id_keys=['working_id']
    )

    datasets = [
        {
            'non_working_id': 'test'
        },
        {

        }
    ]

    ids = [
        generator.generate_from_data(data) for data in datasets
    ]

    assert all(
        current_id == ids[0] for current_id in ids
    )


def test_three_nonidentical_ids():
    generator = ClientIdGenerator(
        id_key='test',
        client_id_keys=['working_id']
    )

    datasets = [
        {
            'working_id': 'test',
            'non_working_id': 'test'
        },
        {
            'working_id': 'test',
        },
        {
            'non_working_id': 'test',
        },
        {

        }
    ]

    ids = [
        generator.generate_from_data(data) for data in datasets
    ]

    assert not all(
        current_id == ids[0] for current_id in ids
    )


def test_two_nested_ids():
    generator = ClientIdGenerator(
        id_key='test',
        client_id_keys=['working_id', 'working.id']
    )

    datasets = [
        {
            'working_id': 'test',
            'working': {
                'id': 'test'
            }
        },
        {
            'working_id': 'test',
            'working': {
                'id': 'test',
                'non_working_id': 'test'
            }
        }
    ]

    ids = [
        generator.generate_from_data(data) for data in datasets
    ]

    assert all(
        current_id == ids[0] for current_id in ids
    )


def test_two_nested_non_identical_ids():
    generator = ClientIdGenerator(
        id_key='test',
        client_id_keys=['working_id', 'working.id']
    )

    datasets = [
        {
            'working_id': 'test',
            'working': {
                'id': 'test'
            }
        },
        {
            'working_id': 'test',
            'working': {
                'id': 'test2',
                'non_working_id': 'test'
            }
        }
    ]

    ids = [
        generator.generate_from_data(data) for data in datasets
    ]

    assert not all(
        current_id == ids[0] for current_id in ids
    )


def test_two_nested_regex_identical_ids():
    # Generator that only matches keys consisting of a-z.a-z, therefore not
    # matching keys containing underscores or numbers.
    generator = ClientIdGenerator(
        id_key='test',
        client_id_keys=['^[a-z]+\\.[a-z]+$']
    )

    datasets = [
        {
            'working_id': 'test',
            'a': {
                'b': 'c',
                '0': '1'
            }
        },
        {
            'non_working_id': 'test',
            'a': {
                'b': 'c'
            }
        }
    ]

    ids = [
        generator.generate_from_data(data) for data in datasets
    ]

    assert all(
        current_id == ids[0] for current_id in ids
    )

