var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/users', usersRouter);

// 🚀 NEW: Here is the "Traffic Cop" for your intermediate page!
app.get('/institution_academic_intermediate', function(req, res) {
  res.render('institution_academic_intermediate');
});
// Route for the Academic Intermediate Page
app.get('/institution_academic_intermediate', function(req, res) {
  res.render('institution_academic_intermediate');
});

// 🚀 NEW: Route for the Student Life Intermediate Page
app.get('/institution_student_life_intermediate', function(req, res) {
  res.render('institution_student_life_intermediate');
});
// Route for the Finance Intermediate Page
app.get('/institution_finance_intermediate', function(req, res) {
  res.render('institution_finance_intermediate');
});

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;