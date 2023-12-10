import express from "express";
import fsp from "fs/promises";
import path from "path";

const areas = JSON.parse(
  await fsp.readFile("../areas.json", { encoding: "utf-8" })
);

/// Don't serve webHidden areas
for (const area in areas) {
  if (areas[area].webHidden) {
    delete areas[area];
  }
}

for (const date of await fsp.readdir("../maps")) {
  for (const map of await fsp.readdir(path.join("../maps", date))) {
    const mapName = path.parse(map).name;
    if (areas[mapName] !== undefined) {
      if (areas[mapName].files === undefined) {
        areas[mapName].files = [];
      }
      areas[mapName].files.push(date);
    }
  }
}

const app = express();
app.get("/list", (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.send(areas);
});
app.get("/map/:name/:date", async (req, res) => {
  try {
    res.setHeader("Access-Control-Allow-Origin", "*");
    const name = req.params.name;
    const date = req.params.date;
    if (name.includes("..") || date.includes("..")) {
      res.status(404);
      res.send("invalid query");
      return;
    }
    if (areas[name] === undefined || areas[name].webHidden) {
      res.status(403);
      res.send("pls don't lag the server");
      return;
    }
    res.type(".png");
    res.send(await fsp.readFile(path.join("../maps", date, name + ".png")));
  } catch (e) {
    res.status(500);
    res.send(e);
  }
});
app.listen(8080);
