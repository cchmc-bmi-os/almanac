import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | cde view footer', function(hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function(assert) {
    let siteQuestion = {
      name: 'Test CDE',
      definition: {
        source_number: 1,
        source_name: 'Test Source',
        source_address: 'http://blag.com',
        version: 1
      },
      choices: [
        {
          source_number: 2,
          source_name: 'Another Test Source',
          source_address: 'http://another.com'
        },
        {
          source_number: 3,
          source_name: 'Third Test Source',
          source_address: 'http://third.com'
        }
      ]
    };
    this.set('siteQuestion', siteQuestion);
    await render(hbs`{{cde-view-footer siteQuestion=siteQuestion}}`);

    assert.ok(find('.cde-footer'), 'it has the root element');
    assert.ok(find('.cde-footer .version'), 'it has a version section');
    assert.ok(find('.cde-footer .sources'), 'it has a sources section');

    assert.equal(findAll('.cde-footer .sources .source').length, 3, 'it has three sources');
  });
});
