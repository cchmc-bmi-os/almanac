import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | saved cde cde', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    this.set('formId', 1);
    this.set('sectionId', 2);
    this.set('cde', 'test_cde');
    await render(hbs`{{saved-cde-cde formId=formId sectionId=sectionId cde=cde}}`);

    assert.ok(find('.cde'));
    assert.equal(find('.cde').textContent.trim(), 'test_cde');
    assert.ok(find('.cde .fa-remove'));
  });
});
