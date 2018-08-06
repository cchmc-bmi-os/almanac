import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | review info card', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    this.set('title', 'Card Title');
    this.set('data', {});
    await render(hbs`{{review-info-card title=title data=data}}`);

    assert.ok(find('.card .card-header').textContent.trim(), 'Card Title', 'it has the correct title');
    assert.ok(find('.card .card-body').textContent.trim(), 'There are no changes', 'it has the correct content');

    this.set('data', {
      test_cde: [
        'Test annotation 1',
        'Test annotation 23',
      ]
    });
    assert.equal(findAll('.card .card-body .text-muted').length, 2, 'it has the two annotations');
    assert.equal(find('.card .card-body h6').textContent.trim(), 'test_cde', 'it has the correct cde name');
  });
});
