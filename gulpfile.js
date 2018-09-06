// Include gulp
var gulp = require('gulp');

// Include Our Plugins
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');


// Compile Our Sass
gulp.task('sass', function() {
    return gulp.src('static/src/sass/*.scss')
        .pipe(sass({indentedSyntax: true}))
        .pipe(gulp.dest('static/build/css'));
});

gulp.task('vendor', function() {
    return gulp.src('static/src/vendor/**')
        .pipe(gulp.dest('static/build/vendor'));
});

gulp.task('js', function() {
    return gulp.src('static/src/js/**')
        .pipe(gulp.dest('static/build/js'));
});

gulp.task('watch', function() {
    return gulp.watch('static/src/**', ['sass', 'js', 'vendor'])
});
