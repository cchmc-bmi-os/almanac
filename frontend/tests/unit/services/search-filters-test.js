import EmberObject from '@ember/object';
import { module, test } from 'qunit';
import { setupTest } from 'ember-qunit';

module('Unit | Service | search filters', function(hooks) {
  setupTest(hooks);

  // Replace this with your real tests.
  test('it exists', function(assert) {
    let service = this.owner.lookup('service:search-filters');
    assert.ok(service);
  });

  test('it has default values', function(assert) {
    let service = this.owner.lookup('service:search-filters');

    ['form', 'section', 'conditionCategory', 'condition', 'site', 'keyword'].forEach((item) => {
      assert.equal(service.get(item), null, `it has the ${item} property`);
    });
  });

  test('it loads, saves, and clears values to the service', function(assert) {
    let service = this.owner.lookup('service:search-filters');

    let section = EmberObject.create({
      id: 1,
      name: 'form_name',
      section: 'section_name',
      fullForm: 'form_name > section_name'
    });

    let filters = {
      form: { name: 'form_name', section: null },
      section,
      conditionCategory: { name: 'cond_cat', label: 'Condition Category' },
      condition: { name: 'cond', label: 'Condition' },
      site: { name: 'site_name', display: 'site_display' },
      keyword: 'keyword',
      keywordWholeWord: false,
      page: 1,
      page_size: 10
    };

    // testing loadFilters function
    service.loadFilters(filters);

    ['form', 'section', 'conditionCategory', 'condition', 'site', 'keyword', 'keywordWholeWord', 'page', 'page_size'].forEach((item) => {
      assert.equal(service.get(item), filters[item], `it has the ${item} property`);
    });

    // testing filters function
    assert.equal(JSON.stringify(service.filters()), JSON.stringify(filters), 'it returns the filters');

    // testing the requestfilters function
    let requestFilters = {
      include: 'form,tags,choices,question',
      form: 'form_name',
      section: 1,
      conditionCategory: 'cond_cat',
      condition: 'cond',
      site: 'site_name',
      keyword: 'keyword',
      keywordWholeWord: false,
      page: 1,
      page_size: 10
    };
    assert.equal(JSON.stringify(service.requestFilters()), JSON.stringify(requestFilters), 'it returns the correct data');

    // testing the saveFilter function
    service.saveFilter('form', 'new-form-val');
    assert.equal(service.get('form'), 'new-form-val', 'it saves the form filter correctly');

    // testing the clearFilter function
    service.clearAllFilters();
    ['form', 'section', 'conditionCategory', 'condition', 'site', 'keyword'].forEach((item) => {
      assert.equal(service.get(item), null, `the ${item} filter is set to null`);
    });
  });
});
