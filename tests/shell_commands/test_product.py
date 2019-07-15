# -*- encoding: utf-8 -*-
#
# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import unicode_literals


def test_prettytable_output(runner):
    product = runner.invoke_raw_parse([
        'product-create',
        '--name', 'foo'])
    assert product['name'] == 'foo'
    show_product = runner.invoke_raw_parse([
        'product-show', product['id']])
    if 'team_id' in show_product:
        product['team_id'] = 'None'
    assert product == show_product
    assert 'etag' not in runner.invoke_raw_parse(['product-list'])
    assert 'etag' in runner.invoke_raw_parse(['product-list', '--long'])


def test_success_create_basic(runner):
    product = runner.invoke(['product-create', '--name',
                             'myproduct'])['product']
    assert product['name'] == 'myproduct'


def test_success_create_full(runner):
    product = runner.invoke(['product-create', '--name', 'myproduct',
                             '--label', 'MYPRODUCT', '--description',
                             'myproduct', '--active'])['product']
    assert product['name'] == 'myproduct'
    assert product['label'] == 'MYPRODUCT'
    assert product['description'] == 'myproduct'
    assert product['state'] == 'active'


def test_create_inactive(runner):
    product = runner.invoke(['product-create', '--name', 'myproduct',
                             '--no-active'])['product']
    assert product['state'] == 'inactive'


def test_list(runner):
    products_number = len(runner.invoke(['product-list'])['products'])

    runner.invoke(['product-create', '--name', 'foo'])
    runner.invoke(['product-create', '--name', 'bar'])

    products_new_number = len(runner.invoke(['product-list'])['products'])

    assert products_new_number == products_number + 2


def test_fail_create_unauthorized_user_admin(runner_user_admin):
    product = runner_user_admin.invoke(['product-create', '--name', 'foo'])
    assert product['status_code'] == 401


def test_fail_create_unauthorized_user(runner_user):
    product = runner_user.invoke(['product-create', '--name', 'foo'])
    assert product['status_code'] == 401


def test_success_update(runner):
    product = runner.invoke(['product-create', '--name', 'foo',
                             '--description', 'foo_desc'])['product']

    result = runner.invoke(['product-update', product['id'],
                            '--etag', product['etag'], '--name', 'bar',
                            '--description', 'bar_desc'])

    assert result['product']['id'] == product['id']
    assert result['product']['name'] == 'bar'
    assert result['product']['description'] == 'bar_desc'


def test_update_active(runner):
    product = runner.invoke(['product-create', '--name',
                             'myproduct'])['product']
    assert product['state'] == 'active'

    result = runner.invoke(['product-update', product['id'],
                            '--etag', product['etag'], '--no-active'])

    assert result['product']['id'] == product['id']
    assert result['product']['state'] == 'inactive'

    result = runner.invoke(['product-update', product['id'],
                            '--etag', result['product']['etag'],
                            '--name', 'foobar'])

    assert result['product']['state'] == 'inactive'

    result = runner.invoke(['product-update', product['id'],
                            '--etag', result['product']['etag'],
                            '--active'])

    assert result['product']['state'] == 'active'


def test_delete(runner):
    product = runner.invoke(['product-create', '--name', 'foo'])['product']

    result = runner.invoke(['product-delete', product['id'],
                            '--etag', product['etag']])

    assert result['message'] == 'Product deleted.'

    result = runner.invoke(['product-show', product['id']])

    assert result['status_code'] == 404


def test_show(runner):
    product = runner.invoke(['product-create', '--name', 'foo'])['product']

    product = runner.invoke(['product-show', product['id']])['product']

    assert product['name'] == 'foo'
