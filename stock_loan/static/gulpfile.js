/**
 * Created by Cameron on 1/3/2016.
 */

var gulp = require('gulp');

var concat = require('gulp-concat');
var css_nano = require('gulp-cssnano');


var uglify = require('gulp-uglify');

var source = require('vinyl-source-stream');
var gutil = require('gulp-util');
var browserify = require('browserify');
var babelify = require('babelify');
var watchify = require('watchify');
var notify = require('gulp-notify');

// var stylus = require('gulp-stylus');
var autoprefixer = require('gulp-autoprefixer');
var buffer = require('vinyl-buffer');

// default task
gulp.task('default', ['scripts', 'watch']);

function handleErrors() {
  var args = Array.prototype.slice.call(arguments);
  notify.onError({
    title: 'Compile Error',
    message: '<%= error.message %>'
  }).apply(this, args);
  this.emit('end'); // Keep gulp from hanging on this task
}

function buildScript(file, watch) {
  var props = {
    entries: ['./src/' + file],
    debug : true,
    cache: {},
    packageCache: {},
    // Turns all experimental features on
    transform:  [babelify.configure({presets : ["react", "es2015", "stage-1"]})]
  };

  // watchify() if watch requested, otherwise run browserify() once
  var bundler = watch ? watchify(browserify(props)) : browserify(props);

  function rebundle() {
    var stream = bundler.bundle();
    return stream
      .on('error', handleErrors)
      .pipe(source(file))
      .pipe(gulp.dest('./build/js/'))
      // If you also want to uglify it
      //.pipe(buffer())
      //.pipe(uglify())
      //.pipe(rename('index.min.js'))
      //.pipe(gulp.dest('./build/js/'))

  }

  // listen for an update and run rebundle
  bundler.on('update', function() {
    rebundle();
    gutil.log('Rebundle...');
  });

  // run it once the first time buildScript is called
  return rebundle();
}

gulp.task('scripts', function() {
  return buildScript('index.js', true); // this will run once because we set watch to false
});



// watch task
gulp.task('watch', function() {
  gulp.watch('./src/sass/*.scss', ['styles']);
  return buildScript('index.js', true); // browserify watch for JS changes
});