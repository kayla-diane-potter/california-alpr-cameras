[out:json][timeout:180];
area["ISO3166-2"="US-CA"]->.ca;
rel(area.ca)["boundary"="administrative"]["admin_level"="6"];
foreach->.c(
  .c out tags;
  .c map_to_area->.a;
  nwr["surveillance:type"="ALPR"](area.a)->.all;
  .all out count;
  nwr.all["manufacturer"="Flock Safety"];
  out count;
);
