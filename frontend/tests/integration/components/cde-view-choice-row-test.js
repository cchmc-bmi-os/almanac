import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, click } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';
import { run } from '@ember/runloop';
import { set } from '@ember/object';

module('Integration | Component | cde view choice row', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    let choice = { text: 'Choice #1', definition: null, source_name: null, source_number: null };
    this.set('choice', choice)

    await render(hbs`{{cde-view-choice-row choice=choice}}`);

    assert.ok(find('.choice'), 'it has a choice');
    assert.notOk(find('.card .card-body'), 'it does not show the card yet');

    await click('.choice');

    assert.ok(find('.card .card-body'), 'it now shows the card');
    assert.equal(find('.card .card-body').textContent.trim(), 'No Definition provided', 'it has the correct choice definition');

    // update the definition
    run(() => {
      set(choice, 'definition', 'Test definition for this cde');
      set(choice, 'source_name', 'Super Secret Source');
      set(choice, 'source_number', 1);
      this.set('choice', choice);

      assert.ok(find('.card .card-body'), 'it now shows the card');
      assert.equal(find('.card .card-body').textContent.trim(), 'Test definition for this cde\n        [1]', 'it has the correct choice definition');
    });
  });
});
