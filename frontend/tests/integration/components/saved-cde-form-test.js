import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, findAll, click } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | saved cde form', function(hooks) {
  setupRenderingTest(hooks);
  /*
  {{saved-cde-form form=form formId=formId}}
  <hr class="form-hr" />
  {{#if savedCdes.isOrdering}}
    <h4 class="form">{{form.name}}</h4>
  {{else}}
    <h4 class="form">
      <i class="text-success fa fa-fw {{expandIcon}}" {{action (toggle 'form.expanded' this)}}></i>
      {{form.name}}
      <i class="text-danger fa fa-remove" {{action 'remove'}}></i>
    </h4>
  {{/if}}
  {{#if expanded}}
    {{#if (not savedCdes.isOrdering)}}
      <ul class="cdes none">
        {{#each noSectionCdes as |cde|}} {{saved-cde-cde formId=formId sectionId=0 cde=cde}} {{/each}}
      </ul>
    {{/if}}
    <div class="section-ordering">
      {{#if savedCdes.isOrdering}}
        {{#sortable-group tagName="div" onChange="updateOrdering" as |group|}}
          {{#each form.sections as |section sectionId|}}
            {{#if section.name}}
              {{#sortable-item tagName="div" model=section group=group}}
                {{saved-cde-section formId=formId section=section sectionId=sectionId}}
              {{/sortable-item}}
            {{/if}}
          {{/each}}
        {{/sortable-group}}
      {{else}}
        {{#each form.sections as |section sectionId|}}
          {{#if section.name}}
            {{saved-cde-section formId=formId section=section sectionId=sectionId}}
          {{/if}}
        {{/each}}
      {{/if}}
    </div>
  {{/if}}


  */

  test('it renders', async function(assert) {
    this.set('form', { name: 'Test Form', expanded: false, sections: [{ name: 'Section #1'}, { name: 'Section #2' }]});
    this.set('formId', 1);
    await render(hbs`{{saved-cde-form form=form formId=formId}}`);

    assert.ok(find('.form-hr'));
    assert.ok(find('.form'));
    assert.equal(findAll('.form .fa').length, 2, 'it has two icons')
    assert.equal(find('.form').textContent.trim(), 'Test Form' , 'it has the correct form name')
    assert.notOk(find('.section-ordering'));

    await click('.form .fa-caret-right');

    assert.ok(find('.section-ordering'));
  });
});
