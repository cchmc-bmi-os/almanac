import $ from 'jquery';
import { isEmpty } from '@ember/utils';
import Service, { inject as service } from '@ember/service';
import { set, computed } from '@ember/object';
import Config from 'almanac/config/environment';

export default Service.extend({
  // the data from the database
  sourceData: null,

  store: service(),

  searchFilters: service('search-filters'),

  session: service(),

  // mapped to the include branching logic checkbox
  includeBranchingLogic: false,

  isOrdering: false,

  hasCdes: computed('count', {
    get() {
      let count = this.get('count');

      return !isNaN(count) && count > 0;
    }
  }),

  /**
   * Returns all of the cdes flattened out for other uses
   *
   * @public
   * @return {array}
   */
  allCdes: computed('sourceData.questions', {
    get() {
      let cdes = null;
      if (this.get('sourceData.questions')) {
        cdes = [];
        this.get('sourceData.questions').forEach((form) => {
          form.sections.forEach((section) => {
            section.cdes.forEach((cde) => {
              cdes.push(cde);
            });
          });
        });
      }

      return cdes;
    }
  }),

  /**
   * This will traverse the data object to count the number of
   * cdes it includes
   *
   * @public
   * @return {int}
   */
  count: computed('allCdes', {
    get() {
      if (this.get('allCdes') === null) {
        return '<i class="fa fa-spinner fa-pulse"></i>';
      }

      return this.get('allCdes').length;
    }
  }),

  /**
   * Removes all saved cdes
   *
   * @public
   */
  clearAll() {
    this.set('sourceData.questions', []);
    this.get('sourceData').save();
  },

  /**
   * Adds a cde to the saved cdes based on the give siteQuestion
   *
   * @public
   * @param {object}
   */
  addCde(siteQuestion) {
    let foundForm = false;
    let foundSection = false;
    let sourceDataQuestions = this.get('sourceData.questions');

    // find form id if exists
    sourceDataQuestions.some((form, formId) => {
      if (form.name === siteQuestion.get('form.name')) {
        foundForm = true;
        sourceDataQuestions[formId].sections.some((section, sectionId) => {
          if (section.name === siteQuestion.get('form.section')) {
            foundSection = true;

            // only add the cde if it doesn't already exists
            if (sourceDataQuestions[formId].sections[sectionId].cdes.indexOf(siteQuestion.get('name')) === -1) {
              sourceDataQuestions[formId].sections[sectionId].cdes.push(siteQuestion.get('name'));
            }
          }

          return foundSection;
        });

        // create just the section
        if (!foundSection) {
          let section = { name: siteQuestion.get('form.section'), cdes: [], expanded: false };
          section.cdes.push(siteQuestion.get('name'));
          sourceDataQuestions[formId].sections.push(section);
        }
      }

      return foundForm;
    });

    // if for did not exist then create the form > section > cde
    if (!foundForm) {
      // create the form object
      let data = { name: siteQuestion.get('form.name'), sections: [], expanded: false };
      // create the section object
      data.sections.push({ name: siteQuestion.get('form.section'), cdes: [], expanded: false });
      // add the cde to the section object
      data.sections[0].cdes.push(siteQuestion.get('name'));

      // add to the main data
      sourceDataQuestions.push(data);
      data = null;
    }

    // save the modified data
    this.set('sourceData.questions', sourceDataQuestions);
    this.get('sourceData').save();
  },

  removeCde(formId, sectionId, cde) {
    let sourceDataQuestions = this.get('sourceData.questions');
    let cdeLocation = sourceDataQuestions[formId].sections[sectionId].cdes.indexOf(cde);

    // check if form or section does not exists
    if (isEmpty(sourceDataQuestions[formId]) || isEmpty(sourceDataQuestions[formId].sections[sectionId])) {
      return;
    }

    if (cdeLocation !== -1) {
      // remove the cde if found
      sourceDataQuestions[formId].sections[sectionId].cdes.splice(cdeLocation, 1);
    }

    // remove the section if it is empty
    if (sourceDataQuestions[formId].sections[sectionId].cdes.length < 1) {
      sourceDataQuestions[formId].sections.splice(sectionId, 1);
    }

    // remove the form if it is empty
    if (sourceDataQuestions[formId].sections.length < 1) {
      sourceDataQuestions.splice(formId, 1);
    }

    // save the modified data
    this.set('sourceData.questions', sourceDataQuestions);
    this.get('sourceData').save();
  },

  removeSection(formId, sectionId) {
    let sourceDataQuestions = this.get('sourceData.questions');

    // check if form or section does not exists
    if (isEmpty(sourceDataQuestions[formId]) || isEmpty(sourceDataQuestions[formId].sections[sectionId])) {
      return;
    }

    // remove the section
    sourceDataQuestions[formId].sections.splice(sectionId, 1);

    // remove the form if it is empty
    if (sourceDataQuestions[formId].sections.length < 1) {
      sourceDataQuestions.splice(formId, 1);
    }

    // save the modified data
    this.set('sourceData.questions', sourceDataQuestions);
    this.get('sourceData').save();
  },

  removeForm(formId) {
    let sourceDataQuestions = this.get('sourceData.questions');

    // check if form or section does not exists
    if (isEmpty(sourceDataQuestions[formId])) {
      return;
    }

    // remove the form
    sourceDataQuestions.splice(formId, 1);

    // save the modified data
    this.set('sourceData.questions', sourceDataQuestions);
    this.get('sourceData').save();
  },

  addAllCdes() {
    let _this = this;
    this.set('addAllInProgress', true);

    $.ajax({
      url: `${Config.api.host}/${Config.api.namespace}/saved-cdes/addall`,
      type: 'get',
      data: _this.get('searchFilters').requestFilters(),
      dataType: 'json',
      success() {
        _this.get('store').find('saved-cde', _this.get('session.data.authenticated.user_id')).then((savedCde) => {
          _this.set('sourceData', savedCde);
        });
        _this.set('addAllInProgress', false);
      }
    });
  },
  expandAll() {
    let _this = this;
    this.set('expandAllInProgress', true);

    $.ajax({
      url: `${Config.api.host}/${Config.api.namespace}/saved-cdes/expandall`,
      type: 'post',
      data: { user_id: _this.get('session.data.authenticated.user_id') },
      dataType: 'json',
      success() {
        _this.get('store').find('saved-cde', _this.get('session.data.authenticated.user_id')).then((savedCde) => {
          _this.set('sourceData', savedCde);
        });
        _this.set('expandAllInProgress', false);
      }
    });
  },
  collapseAll() {
    let _this = this;
    this.set('collapseAllInProgress', true);

    $.ajax({
      url: `${Config.api.host}/${Config.api.namespace}/saved-cdes/collapseall`,
      type: 'post',
      data: { user_id: _this.get('session.data.authenticated.user_id') },
      dataType: 'json',
      success() {
        _this.get('store').find('saved-cde', _this.get('session.data.authenticated.user_id')).then((savedCde) => {
          _this.set('sourceData', savedCde);
        });
        _this.set('collapseAllInProgress', false);
      }
    });
  },
  updateOrder(questions) {
    this.set('sourceData.questions', questions);
  },
  updateSectionOrder(formId, sections) {
    let questions = this.get('sourceData.questions');
    set(questions[formId], 'sections', sections);

    this.set('sourceData.questions', questions);
  },
  resetOrder() {
    this.get('sourceData').rollbackAttributes();
    this.collapseAll();
  },
  saveOrder() {
    this.get('sourceData').save();
    this.collapseAll();
  },
  expandForms() {
    let questions = this.get('sourceData.questions');
    questions.forEach((form, formId) => {
      set(questions[formId], 'expanded', true);
    });
  },
  collapseForms() {
    let questions = this.get('sourceData.questions');
    if (questions) {
      questions.forEach((form, formId) => {
        set(questions[formId], 'expanded', false);
      });
    }
  }
});
