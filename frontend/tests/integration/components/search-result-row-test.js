import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll, click } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | search result row', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    this.set('savedCdes', { allCdes: [] });
    this.set('siteQuestion', {
      classification: null,
      name: 'test_cde',
      text: 'Test CDE',
      form: { fullForm: 'Form > Section' },
      question: {
        definitions: [
          {
            definition: 'This is a test definition',
            definition_note: 'Definition note'
          }
        ]
      }
    });
    await render(hbs`{{search-result-row siteQuestion=siteQuestion savedCdes=savedCdes}}`);

    assert.ok(find('.result'));
    assert.ok(find('.result .action .fa-plus'));
    assert.equal(find('.result .title a').textContent.trim(), 'Test CDE\n         - test_cde');
    assert.equal(find('.result .sub-title').textContent.trim(), 'Form > Section');

    assert.notOk(find('.result .detail'));

    await click('.result .toggle-detail');

    assert.ok(find('.result .detail'));
    assert.ok(findAll('.result .detail label').length, 2);
    assert.ok(findAll('.result .detail p').length, 2);
  });
});
