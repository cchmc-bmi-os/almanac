import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll, click } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | saved cde section', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {

    this.set('formId', 1);
    this.set('section', {
      name: 'Test Section #1',
      expanded: false,
      cdes: [
        'cde1',
        'cde2',
        'cde3'
      ]
    });
    this.set('sectionId', 1);
    await render(hbs`{{saved-cde-section formId=formId section=section sectionId=sectionId}}`);

    assert.ok(find('.section'));
    assert.equal(findAll('.section .fa').length, 2, 'it has two icons')
    assert.equal(find('.section').textContent.trim(), 'Test Section #1');

    assert.notOk(find('.cdes'));

    await click('.section .fa-caret-right');

    assert.ok(find('.cdes'));
  });
});
