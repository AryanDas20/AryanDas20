![](https://komarev.com/ghpvc/?username=your-github-username&color=blueviolet)
import React, { useState } from "react";
import ReactDOM from "react-dom";
import ReactMarkdown from "react-markdown";
import MarkNav from "markdown-navbar";
import article from "./article";

import "markdown-navbar/dist/navbar.css";
import "./styles.css";

function App() {
  const [navVisible, setNavVisible] = useState(true);

  return (
    <div className="App">
      <div className="article-container">
        <ReactMarkdown source={article} />
      </div>
      <div className={`nav-container ${navVisible ? "show" : "hide"}`}>
        <div
          className="toggle-btn"
          onClick={() => {
            setNavVisible(!navVisible);
          }}
        >
          {navVisible ? "MENU →" : "← MENU"}
        </div>
        <MarkNav source={article} />
      </div>
    </div>
  );
}

const rootElement = document.getElementById("root");
ReactDOM.render(<App />, rootElement);

### Hi there 👋

**AryanDas20/AryanDas20** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- _ 🔭 I’m currently working on php projects
- _ 🌱 I’m currently learning php and react
- _ 📫 I deploy My Websites In Netlify 
[![Netlify Status](https://api.netlify.com/api/v1/badges/c9636386-1bac-4321-ac59-1b4e475f5c12/deploy-status)](https://app.netlify.com/sites/aryandas/deploys)
- :apple: I Currently study In class IX at :books: kendriya vidyalaya. 
[CLICK THIS LINK TO SEE MY CERTIFICATES](https://github.com/AryanDas20/Resume)
![Aryan's GitHub stats](https://github-readme-stats.vercel.app/api?username=AryanDas20&show_icons=true&theme=radical)

[![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=anuraghazra&layout=compact)](https://aryandas.netlify.app/)
![img](file:///C:/Dev/Aryan_HTML/qrcode_aryandas.netlify.app%20(1).png)
