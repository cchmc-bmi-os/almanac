import { module, test } from 'qunit';
import { setupRenderingTest } from 'ember-qunit';
import { render, find, click } from '@ember/test-helpers';
import hbs from 'htmlbars-inline-precompile';

module('Integration | Component | filter text', function(hooks) {
  setupRenderingTest(hooks);

  /*
  {{filter-text
    name="keyword"
    label="Keyword"
    value=searchFilters.keyword
    wholeWord=searchFilters.keywordWholeWord
    popover="Text here" }}

  <div class="filter form-group">
    <label>
        {{label}}
        <a class="da-popover" onclick="return false;" href="#"><i class="fa fa-question-circle"></i></a>
      </label>
    <div class="pull-right">
      <label class="whole-word-label" for="whole_word">Match whole word</label> {{input type="checkbox" name="wholeWord" checked=wholeWord
      change=(action "updateFilters" value wholeWord)}}
    </div>
    {{#if value}}
    <span class="ember-power-select-clear-btn clear-btn-keyword" {{action 'updateFilters' null}}>×</span> {{!-- <i class="fa fa-remove clear-btn-keyword"></i>  --}} {{/if}} {{input type="text" class="form-control" value=value key-up=(action "updateFilters")}}
  </div>
  */

  test('it renders', async function(assert) {
    this.set('name', 'filter_name');
    this.set('value', 'fname');
    this.set('label', 'Filter Name');
    this.set('wholeWord', false);
    this.set('popover', 'This is the pop over text');

    await render(hbs`{{filter-text name=name label=label value=value wholeWord=wholeWord popover=popover}}`);

    assert.ok(find('.filter.form-group'));
    assert.ok(find('.filter.form-group .pull-right'));
    assert.equal(find('.filter.form-group label').textContent.trim(), 'Filter Name', 'it has the right label');
    assert.equal(find('.filter .pull-right .whole-word-label').textContent.trim(), 'Match whole word');
    assert.equal(find('.filter .pull-right input').checked, false, 'whole word is not checked');

    await click('.filter .pull-right input');

    assert.equal(find('.filter .pull-right input').checked, true, 'whole word is now checked');
  });
});
