import { module, test } from 'qunit';
import { visit, currentURL, currentRouteName, findAll } from '@ember/test-helpers';
import { setupApplicationTest } from 'ember-qunit';

module('Acceptance | help page', function(hooks) {
  setupApplicationTest(hooks);

  test('the help page had the correct elements', async function(assert) {
    await visit('/help');

    assert.equal(currentURL(), '/help');
    assert.equal(currentRouteName(), 'help');

    assert.equal(findAll('#toc').length, 1, 'it has a #toc id');
    assert.equal(findAll('#filter').length, 1, 'it has a #filter id');
    assert.equal(findAll('#filter-all').length, 1, 'it has a #filter-all id');
    assert.equal(findAll('#filter-categories').length, 1, 'it has a #filter-categories id');
    assert.equal(findAll('#filter-count-search').length, 1, 'it has a #filter-count-search id');
    assert.equal(findAll('#filter-help').length, 1, 'it has a #filter-help id');
    assert.equal(findAll('#search-results').length, 1, 'it has a #search-results id');
    assert.equal(findAll('#search-results-cde').length, 1, 'it has a #search-results-cde id');
    assert.equal(findAll('#search-results-paginate').length, 1, 'it has a #search-results-paginate id');
    assert.equal(findAll('#saved-cdes').length, 1, 'it has a #saved-cdes id');
    assert.equal(findAll('#saved-cdes-panel').length, 1, 'it has a #saved-cdes-panel id');
    assert.equal(findAll('#saved-cdes-expanding').length, 1, 'it has a #saved-cdes-expanding id');
    assert.equal(findAll('#saved-cdes-order').length, 1, 'it has a #saved-cdes-order id');
  });
});
