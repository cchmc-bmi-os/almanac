import { helper } from '@ember/component/helper';

export function numberFormat(params/* , hash */) {
  let [string] = params;
  return string.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

export default helper(numberFormat);
