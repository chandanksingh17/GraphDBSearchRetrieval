const config = {
  container_id: "graph",
  server_url: "bolt://18.117.88.210:7687",
  server_user: "neo4j",
  server_password: "neo4jneo4j", // user , user only have read access! So safe to put it here
  labels: {
    Strain: {
      caption: "name",
      size: "id",
      community: "type_id",
    },
  },
  relationships: {
    DISTANCE: {
      thickness: "value",
      caption: false,
    },


  },
  initial_cypher: `MATCH p=(s1:Strain)-[r:DISTANCE]->(s2:Strain) RETURN *`,
};

var driver = neo4j.driver(
  "bolt://18.117.88.210:7687",
  neo4j.auth.basic("neo4j", "neo4jneo4j")
);

function draw(name, subType, relationType, value) {
  const strainName = name === "All" ? "" : `{name:'${name}'}`;
 /// const relation = relationType == 1 ? "SEQUENCE_SIMILARITY" : "DISTANCE";
  ///const relation = relationType == "1" ? "SEQUENCE_SIMILARITY" :(relationType=="0" ? "DISTANCE":"HI_TITER_VALUE");
  const relation = relationType == "1" ? "" :"GENETIC_DISTANCE";
  //const operatorString = operator == 1 ? "<=" : ">=";
 // const operatorString = "=";
  const operatorQuery =
    //value === "" ? "" : `r.value ${operatorString} ${value}`;
      value === "" ? "" : `${value}`;
  ///
  const subTypeString =
    subType === "All"
      ? ""
      : `s1.type = '${subType}' AND s2.type = '${subType}'`;
  const whereCause =
    subTypeString !== "" || operatorQuery !== ""
      ? ` LIMIT${subTypeString} ${operatorQuery}`
      :  `LIMIT 1500`;
  const cipher = `MATCH p=(s1:Strain${strainName})-[r:${relation}]->(s2:Strain) RETURN p ORDER BY r.value ${whereCause} `;
  //const cipher = `MATCH p=()-[r:GENETIC_DISTANCE]->() RETURN p LIMIT 25`;
//WHERE ${subTypeString} ${operatorQuery}
  console.log(cipher);
  graph.renderWithCypher(cipher);
}

function filter() {
  setLoading(true);
  const subType = document.getElementById("subType").value;
  const relationType = document.getElementById("relationType").value;
  const optionValue = document.getElementById("optionValue").value;
  //const operator = document.getElementById("operator").value;
  const name = document.getElementById("name").value;
  //draw(name, subType, relationType, optionValue, operator);
  draw(name, subType, relationType, optionValue);
}

function clearFilter() {
  setLoading(true);
  document.getElementById("subType").value = "All";
  document.getElementById("relationType").value = 0;
  document.getElementById("optionValue").value = "";
  //document.getElementById("operator").value = 0;
  graph.renderWithCypher(config.initial_cypher);
}

function render_completed() {
  setTimeout(function () {
    setLoading(false);
  }, 4000);
}

function setLoading(status) {
  const loading = document.getElementById("loading");
  if (status) {
    loading.style.display = "block";
  } else {
    loading.style.display = "none";
  }
}

function loadRegions() {
  let session = driver.session();
  let readTxResultPromise = session.readTransaction((txc) => {
    return txc.run(
      "MATCH p=(s1:Strain)-[]-(s2:Strain) WHERE s1.region IS NOT NULL RETURN DISTINCT s1.region LIMIT 1500;"
    );
  });

  // returned Promise can be later consumed like this:
  readTxResultPromise
    .then((result) => {
      let data = [{ id: "All", text: "All" }];
      result.records.forEach(function (record, index) {
        data.push({ id: record._fields[0], text: record._fields[0] });
      });
      $("#region").select2({ placeholder: "Search region", data: data });
    })
    .catch((error) => {
      console.log(error);
    })
    .then(() => session.close());
}

function loadStrains() {
  let session = driver.session();
  let readTxResultPromise = session.readTransaction((txc) => {
    return txc.run(
      "MATCH p=(s1:Strain)-[]-(s2:Strain) RETURN DISTINCT s1.name LIMIT 1500;"
    );
  });

  // returned Promise can be later consumed like this:
  readTxResultPromise
    .then((result) => {
      let data = [{ id: "All", text: "All" }];
      result.records.forEach(function (record, index) {
        data.push({ id: record._fields[0], text: record._fields[0] });
      });
      $("#name").select2({ placeholder: "Search strain", data: data });
    })
    .catch((error) => {
      console.log(error);
    })
    .then(() => session.close());
}

var graph = new NeoVis.default(config);
graph.registerOnEvent("completed", render_completed);
graph.render();

$(document).ready(function () {
  loadRegions();
  loadStrains();
  setTimeout(function () {
    filter();
  }, 2000);
});

$(".toggle_button").click(function () {
  if ($(".filter_box").hasClass("hide")) {
    $(".filter_box").removeClass("hide");
    $(".toggle_button").html('<i class="far fa-times-circle"></i>');
  } else {
    $(".filter_box").addClass("hide");
    $(".toggle_button").html('<i class="fas fa-cogs"></i>');
  }
});
