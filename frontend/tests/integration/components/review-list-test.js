import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | review list', function(hooks) {
  setupRenderingTest(hooks);

  hooks.beforeEach(function() {
    this.actions = {};
    this.send = (actionName, ...args) => this.actions[actionName].apply(this, args);
  });

  test('it renders', async function(assert) {
    this.set('data', []);
    this.set('label', 'Test Label');
    this.actions.refresh = () => {
      return true;
    };
    this.actions.remove = () => {
      return true;
    };
    this.actions.requestRemoval = () => {
      return true;
    };

    await render(hbs`{{review-list data=data label=label}}`);

    assert.ok(find('.review-list'));
    assert.equal(find('.review-list .text-primary').textContent.trim(), 'Test Label', 'it has the correct label');
    assert.ok(find('.review-list .table'));
    assert.equal(findAll('.review-list .table td').length, 1, 'it only has one cell in the table');
    assert.equal(find('.review-list .table tr td').textContent.trim(), 'There are no completed reviews');

    this.set('data', [
      { name: 'Test Review', started_at: '2016-10-11 13:23:43', user: { fullname: 'Test User' }, status: 'CCHMC Review', isComplete: false, isReadyForAnnotation: true }
    ]);

    assert.equal(findAll('.review-list .table td').length, 5, 'it now has 5 columns in the table');
  });
});
