const express = require('express');
const session = require('express-session');
const fs = require('fs');
const path = require('path');
const app = express();
const courses_list = require('./course.json');

const dummy = {
    name: 'Course Name',
    available: true,
    taken: false,
    description: '',
    cost: 1,
};

courses_list['DSA'] = {
    name: 'DSA',
    available: false,
    taken: false,
    description: fs.readFileSync('flag.txt', 'utf8').trim(),
    cost: 3,
};

app.use(express.static(path.join(__dirname, 'public')));
app.set('view engine', 'ejs');
app.use(express.json({ extended: true }));

app.use(session({
    secret: require('crypto').randomBytes(64).toString('hex'),
    resave: false,
    saveUninitialized: true,
}));

app.use((req, res, next) => {
    if (req.ip == '127.0.0.1') {
        req.session.admin = true;
    }

    if (!req.session.courses) {
        req.session.courses = courses_list;
    }
    next();
});

app.get('/', (req, res) => {
    res.render('index', { courses: req.session.courses });
});

app.get('/edit-irs', (req, res) => {
    res.render('edit-irs', { courses: req.session.courses });
});

app.get('/admin', (req, res) => {
    if (!req.session.admin) {
        return res.status(404).send('Not an Admin');
    } else {
        res.render('admin', { courses: req.session.courses });
    }
});

app.post('/api/v1/edit-irs', (req, res) => {
    for (const [key, value] of Object.entries(req.body)) {
        if (!req.session.courses[key]) {
            req.session.courses[key] = JSON.parse(JSON.stringify(dummy));
        }

        for (const [k, v] of Object.entries(value)) {
            if (!req.session.admin && (k === 'available' || req.session.courses[key].available === false)) {
                continue;
            } else {
                req.session.courses[key][k] = v;
            }
        }
    }

    res.send('Successfully updated');
});

app.listen(3000, () => {
    console.log(`Listening at http://127.0.0.1:3000`);
});