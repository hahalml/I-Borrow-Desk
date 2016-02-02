const utils = {
  toPercentage: x => {
    return `${((x) * 100).toFixed(1)} %`;
  },

  toPercentageNoScale: x => {
    return `${x.toFixed(1)}%`;
  },

  toCommas: x => {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  },

  showWarning: (field) => {
    if (field.touched && field.invalid) return 'has-danger';
  }
};

export default utils;