import EmberObject from '@ember/object';
import Service from '@ember/service';
import { run } from '@ember/runloop';
import { typeOf, isEmpty } from '@ember/utils';

export default Service.extend({
  // the form filter @type {object}
  form: null,

  // the section filter @type {object}
  section: null,

  // the condition category filter @type {object}
  conditionCategory: null,

  // the condition filter @type {object}
  condition: null,

  // the site filter @type {object}
  site: null,

  // the keyword filter @type {object}
  keyword: null,

  // the keyword filter @type {object}
  keywordWholeWord: false,

  // the current page variable @type {int}
  page: 1,

  // the page size variable @type {int}
  page_size: 10,

  /**
   * Clear all of the filters
   *
   * @public
   */
  clearAllFilters() {
    // clear all the filters
    run(() => {
      this.set('section', null);
      this.set('form', null);
      this.set('condition', null);
      this.set('conditionCategory', null);
      this.set('site', null);
      this.set('keyword', null);
      this.set('keywordWholeWord', false);
      this.set('page', 1);
      this.set('page_size', 10);
    });

    this._storeFilters();
  },

  /**
   * Save the given filter with the give value
   *
   * @public
   * @param  {string} name
   * @param  {object} value
   */
  saveFilter(filter, value) {
    this.set(filter, value);

    switch (filter) {
      case 'form':
        if (!isEmpty(value)) {
          this.set('section', null);
        }
        break;
      case 'section':
        this.set('form', value);
        break;
      case 'conditionCategory':
        this.set('condition', null);
        break;
    }

    this._storeFilters();
  },

  /**
   * Save all of the filters to localStorage
   *
   * @private
   */
  _storeFilters() {
    let filters = this.filters();

    // store the filters to localStorage
    window.localStorage.setItem('filters', JSON.stringify(filters));
  },

  /**
   * Load all the filters from localStorage
   *
   * @public
   */
  loadFilters(filters) {
    // load from localStorage if filters is not specified
    if (!filters) {
      filters = JSON.parse(window.localStorage.getItem('filters'));
    }

    // lets make sure that the filters exist from loading from localStorage
    if (!filters) {
      filters = {};
    }

    // if there is data, set the data
    this.set('form', filters.form || null);
    this.set('section', filters.section || null);
    this.set('conditionCategory', filters.conditionCategory || null);
    this.set('condition', filters.condition || null);
    this.set('site', filters.site || null);
    this.set('keyword', filters.keyword || null);
    this.set('keywordWholeWord', filters.keywordWholeWord || false);
    this.set('page_size', filters.page_size || 10);
    this.set('page', filters.page || 1);
  },

  /**
   * Return all of the filters in an object
   *
   * @public
   * @return {object}
   */
  filters() {
    // handle custom logic for the section to include some other info
    let section = this.get('section');
    if (section !== null) {
      if (typeOf(section) !== 'instance') {
        section = EmberObject.create(section);
      }
      section = { id: section.id, name: section.get('name'), section: section.get('section'), fullForm: section.get('fullForm') };
    }

    // setup the filters to be stored
    return {
      form: this.get('form'),
      section,
      conditionCategory: this.get('conditionCategory'),
      condition: this.get('condition'),
      site: this.get('site'),
      keyword: this.get('keyword'),
      keywordWholeWord: this.get('keywordWholeWord'),
      page: this.get('page'),
      page_size: this.get('page_size')
    };
  },

  /**
   * Returns the filters that are needed to make a request to the API
   *
   * @public
   * @return {object}
   */
  requestFilters() {
    let filters = this.filters();
    if (filters) {
      filters = JSON.parse(JSON.stringify(filters));
    }

    return {
      include: 'form,tags,choices,question',
      form: isEmpty(filters.form) ? null : filters.form.name,
      section: isEmpty(filters.section) ? null : filters.section.id,
      conditionCategory: isEmpty(filters.conditionCategory) ? null : filters.conditionCategory.name,
      condition: isEmpty(filters.condition) ? null : filters.condition.name,
      site: isEmpty(filters.site) ? null : filters.site.name,
      keyword: isEmpty(filters.keyword) ? null : filters.keyword,
      keywordWholeWord: isEmpty(filters.keywordWholeWord) ? false : filters.keywordWholeWord,
      page: isEmpty(filters.page) ? 1 : filters.page,
      page_size: isEmpty(filters.page_size) ? 10 : filters.page_size
    };
  }
});
