var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { 
    title: 'UCAR | University Interface',
    year: '2026' 
  });
});

module.exports = router;
