const element = document.getElementById('wikimedia');


async function wikiElement(){
    // Set WIKIMEDIA_DATE to YYYY/MM/DD to pull top pageviews from a specific day.
    const WIKIMEDIA_DATE = "YYYY/MM/DD";
    const url = `https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/${WIKIMEDIA_DATE}`;

    const res = await fetch(url);

    if(!response.ok){throw new Error(`Error Code ${response.status}: ${response.statusText}`)}

    const data = res.json();

    element.children[0].innerHTML = `${data.items[0].articles.slice(980,1000)}`
}

// {"article":"Val_Kilmer","views":10581,"rank":970},
// {"article":"List_of_most-streamed_artists_on_Spotify","views":10570,"rank":971},
// Weightlifting_at_the_2022_Asian_Games
// {"article":"Billie_Eilish","views":10565,"rank":972},
// {"article":"Lisa_Marie_Presley","views":10549,"rank":974},
// {"article":"Robert_Downey_Jr.","views":10548,"rank":975},
// {"article":"2024_Summer_Olympics","views":10547,"rank":976},
// Talking_Heads
// {"article":"Salma_Hayek","views":10543,"rank":978},
// Mutulu_Shakur
// {"article":"Fleetwood_Mac","views":10527,"rank":980},
// {"article":"Wrexham_A.F.C.","views":10527,"rank":980},
// Suella_Braverman
// {"article":"Richard_Winters","views":10523,"rank":983},
// {"article":"Squash_at_the_2022_Asian_Games_–_Men's_team","views":10517,"rank":984},
// {"article":"Paris_Saint-Germain_F.C.","views":10509,"rank":985},
// {"article":"Brittany_Murphy","views":10505,"rank":986},
// {"article":"Henry_VIII","views":10503,"rank":987},
// {"article":"Millennials","views":10498,"rank":988},
// {"article":"Ana_de_Armas","views":10498,"rank":988},
// {"article":"Jason_Momoa","views":10493,"rank":990},
// {"article":"Kevin_Costner","views":10487,"rank":991},
// {"article":"James_Dean","views":10487,"rank":991},
// {"article":"Rachel_McAdams","views":10477,"rank":993},
// {"article":"Emily_Blunt","views":10475,"rank":994},
// {"article":"Vande_Bharat_Express","views":10459,"rank":995},
// {"article":"Natalie_Portman","views":10455,"rank":996},
// {"article":"Penélope_Cruz","views":10441,"rank":997},
// {"article":"Kacie_McDonnell","views":10422,"rank":998},
// {"article":"Dmitry_Bivol","views":10409,"rank":999},
// Roblox