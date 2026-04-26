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
// Route for the HR Intermediate Page
app.get('/institution_hr_intermediate', function(req, res) {
  res.render('institution_hr_intermediate');
});
// Route for the ESG Intermediate Page
app.get('/institution_esg_intermediate', function(req, res) {
  res.render('institution_esg_intermediate');
});
// Route for the Infrastructure Intermediate Page
app.get('/institution_infrastructure_intermediate', function(req, res) {
  res.render('institution_infrastructure_intermediate');
});
// Route for the Research Intermediate Page
app.get('/institution_research_intermediate', function(req, res) {
  res.render('institution_research_intermediate');
});
// Route for the Partnerships Intermediate Page
app.get('/institution_partnerships_intermediate', function(req, res) {
  res.render('institution_partnerships_intermediate');
});
// Route for Employment / Insertion Professionnelle
app.get('/institution_employment_intermediate', function(req, res) {
  res.render('institution_employment_intermediate');
});
// Route for the KPI Menu Intermediate Page
app.get('/kpi_menu_intermediate', function(req, res) {
  res.render('kpi_menu_intermediate');
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