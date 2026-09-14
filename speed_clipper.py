# ---------------------------------------------------------------------
# SpeedClipper - Playwright Speed Run designer for Universal Paperclips
# www.decisionproblem.com/paperclips/
# ---------------------------------------------------------------------

from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from playwright.sync_api import sync_playwright
import json
import time

save_file = 'uclips_save.json'
start_time = time.perf_counter()

log = []
milestones = [
    "clips created",
    "Quantum computing online",
    "Full autonomy attained",
    "Clips Created",
    "Terrestrial resources fully utilized"
]

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def get_int(locator):
    """Remove commas and return integer value"""
    value = locator.inner_text().replace(",", "")
    try:
        return int(value)
    except ValueError:
        return 0

def get_float(locator):
    """Remove commas and return float value"""
    value = locator.inner_text().replace(",", "")
    try:
        return float(value)
    except ValueError:
        return 0.0

def read_values(page):
    values = page.evaluate("""
        var gameStats = {
    
            console1: readoutElement1.innerHTML,
            clips: Math.round(clips),

            funds: funds,
            avgRev: avgRev || 0.00,
            clip_price: margin,
            unsold_clips: Math.round(unsoldClips),
            marketing_level: marketingLvl,
            demand: Math.round(demand) * 10,

            clips_per_second: clipmakerRate,
            wire: Math.round(wire),
            wire_cost: wireCost,
            autoclippers: clipmakerLevel,
            megaclippers: megaClipperLevel,
            // minimumPrice: (wireBasePrice + 10) / wireSupply,

            trust: trust,
            processors: processors,
            memory: memory,
            creativity: creativity,
            tempOps: tempOps,
            qchip_value: qChips[0].value,
            qchip_active: qChips[0].active,
            
            port_value: portTotal,
            invst_lvl: investLevel,
            invst_risk: investStratElement.value,
            bribe: bribe,
            
            yomi: yomi,

            //flags
            creativityOn: creativityOn,
            strategyEngineFlag: strategyEngineFlag,
            investmentEngineFlag: investmentEngineFlag,
            releasedHypnoDrones: project35.flag
        }
        gameStats 
        """)
    
    # dropdown values
    values["strat_level"] = page.locator("#stratPicker").input_value()
    values["invst_risk"] = page.locator("#investStrat").input_value()

    console1 = values["console1"]
    if any(milestone in console1 for milestone in milestones):
        if console1 not in log:
            log.append(console1)
            log_time = time.perf_counter() - start_time
            print(f"{format_time(log_time)} - {console1}")

    return values

def get_completed_projects(page):
    projects = page.evaluate("projects")
    completed_projects = []
    for p in projects:
        p["id"].replace("projectButton", "")
        if p["flag"] == '1':
            completed_projects.append(p["id"])
    return completed_projects

def rapid_click(page, button_id, clicks):
    page.evaluate(
        """
        ({ buttonId, clicks }) => {
            const button = document.getElementById(buttonId);
            if (!button) throw new Error(`Button "${buttonId}" not found`);
            for (let i = 0; i < clicks; i++) button.click();
        }
        """,
        {"buttonId": button_id, "clicks": clicks},
    )

def click_projects(page, project_ids):
    for project_id in project_ids:
        prj_button = page.locator(f"#projectButton{project_id}")
        if prj_button.count() > 0 and prj_button.is_enabled():
            prj_button.click()
            log_time = time.perf_counter() - start_time
            print(f"{format_time(log_time)} - Project {project_id} clicked")

# ---------------------------------------------------------------------------
# Strategy config
#
# Each stage is just a dict with:
#   "exit"    : function(stats) -> bool         (when to move to next stage)
#   "rules"   : list of (name, condition, action) tuples, checked in order
#   "projects": list of project ids to poll each tick
#   "tick"    : optional function() -> None, run once per loop before reading stats
# ---------------------------------------------------------------------------

def make_stages(page):
    #Buttons
    raise_clip_price = page.locator("#btnRaisePrice")
    lower_clip_price = page.locator("#btnLowerPrice")
    buy_wire = page.locator("#btnBuyWire")
    btnAddProc = page.locator("#btnAddProc")
    btnAddMem = page.locator("#btnAddMem")
    btnMarketing = page.locator("#btnExpandMarketing")
    btnMakeClipper = page.locator("#btnMakeClipper")
    btnMakeMegaClipper = page.locator("#btnMakeMegaClipper")
    btnToggleWireBuyer = page.locator("#btnToggleWireBuyer")
    btnInvest = page.locator("#btnInvest")
    btnWithdraw = page.locator("#btnWithdraw")
    btnNewTournament = page.locator("#btnNewTournament")
    btnRunTournament = page.locator("#btnRunTournament")
    btnImproveInvestments = page.locator("#btnImproveInvestments")
    
    stages = [
        {
            "name": "Setup Clip Price",
            "exit": lambda s: s["clip_price"] <= 0.03,
            "rules": [
                ("lower_price",
                 lambda s: s["clip_price"] > 0.03,
                 lower_clip_price.click),
            ],
        },
        {
            "name": "Enable Quantum Computing",
            "exit": lambda s: s["qchip_active"] != 0,
            "tick": lambda: rapid_click(page, "btnMakePaperclip", 500),
            "rules": [
                ("wirebuyer_stage1",
                 lambda s: s["wire"] < 100
                 and s["clips"] < 450_000
                 and buy_wire.is_enabled(),
                 buy_wire.click),
                ("add_processors_to_5",
                 lambda s: s["processors"] < 5 and btnAddProc.is_enabled(),
                 btnAddProc.click),
                ("add_memory_to_10",
                 lambda s: s["processors"] >= 5
                 and s["memory"] < 10
                 and btnAddMem.is_enabled(),
                 btnAddMem.click),
                ("raise_price_high_demand",
                 lambda s: s["clips"] < 450_000 and s["demand"] > 1000,
                 raise_clip_price.click),
                ("raise_price_prep_next_stage",
                 lambda s: s["clips"] >= 450_000 and s["clip_price"] < 0.20,
                 raise_clip_price.click),
                ("bump_up_marketing_to_5",
                 lambda s: s["clips"] >= 450_000 and s["marketing_level"] < 5
                 and btnMarketing.is_enabled(),
                 btnMarketing.click),
                ("wirebuyer_stage2",
                 lambda s: s["clips"] >= 450_000
                 and s["unsold_clips"] < 10_000
                 and s["wire"] < 100
                 and buy_wire.is_enabled(),
                 buy_wire.click),
            ],
            # P3/P6/P13/P14: +1 trust. P12/P34: Hypno Harmonics strategy.
            # P50/P51: Quantum Computing / first qChip.
            "projects": [3, 6, 12, 13, 14, 34, 50, 51],
        },
        {
            "name": "Bulk upgrade and Strategy Engine unlock",
            "exit": lambda s: page.locator("#strategyEngine").is_visible(),
            "rules": [
                ("qcompute",
                 lambda s: s["qchip_value"] > 0.1,
                 lambda: rapid_click(page, "btnQcompute", 500)),
                ("wirebuyer_manual",
                 lambda s: not btnToggleWireBuyer.is_visible()
                 and s["unsold_clips"] < 15_000
                 and s["wire"] < 100
                 and buy_wire.is_enabled(),
                 buy_wire.click),
                ("max_autoclippers",
                 lambda s: s["autoclippers"] < 75 
                 and btnMakeClipper.is_enabled(),
                 btnMakeClipper.click),
                ("increase_megaclippers",
                 lambda s: btnMakeMegaClipper.is_visible()
                 and s["megaclippers"] < 10
                 and btnMakeMegaClipper.is_enabled(),
                 btnMakeMegaClipper.click),
                ("add_processors_to_15",
                 lambda s: s["processors"] < 15 and btnAddProc.is_enabled(),
                btnAddProc.click),
                ("increase_marketing",
                 lambda s: s["marketing_level"] < 8 and btnMarketing.is_enabled(),
                 btnMarketing.click),
                ("reduce_price_on_wirebuyer",
                 lambda s: btnToggleWireBuyer.is_visible()
                 and s["clip_price"] > 0.05,
                 lower_clip_price.click),
            ],
            # P21 trading, P22 tournaments/Yomi
            "projects": [42, 26, 1, 4, 5, 7, 8, 9, 10, 11, 16, 19, 20, 21, 22, 23, 24, 25, 70, 12, 34],
        },
        {
            "name": "Build Yomi and investment up to 1.2M",
            "exit": lambda s: s["port_value"] >= 1_200_000,
            "rules": [
                ("qcompute",
                 lambda s: s["qchip_value"] > 0.1,
                 lambda: rapid_click(page, "btnQcompute", 500)),
                ("random_strat",
                 lambda s: s["strat_level"] != 0,
                 lambda: page.locator("#stratPicker").select_option("0")),
                ("new_tournament",
                 lambda s: btnNewTournament.is_enabled(),
                 btnNewTournament.click),
                ("run_tournament",
                 lambda s: btnRunTournament.is_enabled(),
                 btnRunTournament.click),
                ("add_processors_to_75",
                 lambda s: s["processors"] < 75 and btnAddProc.is_enabled(),
                btnAddProc.click),
                ("add_memory_to_25",
                 lambda s: s["processors"] >= 75
                 and s["memory"] < 25
                 and btnAddMem.is_enabled(),
                 btnAddMem.click),
                ("increase_marketing_6",
                 lambda s: s["marketing_level"] < 5 and btnMarketing.is_enabled(),
                 btnMarketing.click),
                ("lower_price_to_0.03",
                 lambda s: s["clip_price"] > 0.03,
                 lower_clip_price.click),
                ("Increase_investment_level_6",
                 lambda s: s["invst_lvl"] < 6 and btnImproveInvestments.is_enabled(),
                 btnImproveInvestments.click),
                ("Set_risk_med_below_lvl_4",
                 lambda s: s["invst_lvl"] < 6
                 and s["invst_risk"] != "med",
                 lambda: page.locator("#investStrat").select_option("med")),
                ("Set_risk_high_after_lvl_6",
                 lambda s: s["invst_lvl"] >= 6
                 and s["invst_risk"] != "hi",
                 lambda: page.locator("#investStrat").select_option("hi")),
                ("funnel_funds_to_investment_1.2M",
                 lambda s: btnInvest.is_enabled()
                 and s["funds"] >= 500
                 and s["wire"] >= 1000,
                 btnInvest.click),

                # 14,15,17 +1 trust (creat-trust), 
                # P28 Cure Cancer, +1 T (ops-trust)
                # P30 Global Warming +15 T (4.5kyomi-trust)
                # P29 World Peace +1 T (15kyomi-trust)
                # P31 Male Baldness +20 T (ops)
                # P37 HOSTILE TAKEOVER ($1M)
            ],
            "projects": [15, 16, 17, 27, 28, 29, 30, 31, 37],
        },
        {
            "name": "Reach Hostile takeover",
            "exit": lambda s: s["console1"] == "Global Fasteners acquired, public demand increased x5",
            "rules": [
                ("qcompute",
                 lambda s: s["qchip_value"] > 0.1,
                 lambda: rapid_click(page, "btnQcompute", 500)),
                ("new_tournament",
                 lambda s: btnNewTournament.is_enabled(),
                 btnNewTournament.click),
                ("run_tournament",
                 lambda s: btnRunTournament.is_enabled(),
                 btnRunTournament.click),
                ("add_processors_to_75",
                 lambda s: s["processors"] < 75 and btnAddProc.is_enabled(),
                btnAddProc.click),
                ("add_memory_to_25",
                 lambda s: s["processors"] >= 75
                 and s["memory"] < 25
                 and btnAddMem.is_enabled(),
                 btnAddMem.click),
                ("Increase_investment_level_6",
                 lambda s: s["invst_lvl"] < 6 and btnImproveInvestments.is_enabled(),
                 btnImproveInvestments.click),
                ("Withdraw_funds_to_achieve_hostile_takeover",
                 lambda s: s["funds"] < 1_000_000
                 and btnWithdraw.is_enabled(),
                 btnWithdraw.click),
            ],
                # 29,30,31 hi T reward projects
                # P37 HOSTILE TAKEOVER ($1M)
            "projects": [29, 37],
        },
        {
            "name": "Build funds up to 12M",
            "exit": lambda s: s["port_value"] >= 12_000_000,
            "rules": [
                ("qcompute",
                 lambda s: s["qchip_value"] > 0.1,
                 lambda: rapid_click(page, "btnQcompute", 500)),
                ("new_tournament",
                 lambda s: btnNewTournament.is_enabled(),
                 btnNewTournament.click),
                ("run_tournament",
                 lambda s: btnRunTournament.is_enabled(),
                 btnRunTournament.click),
                ("add_processors_to_75",
                 lambda s: s["processors"] < 75 and btnAddProc.is_enabled(),
                btnAddProc.click),
                ("add_memory_to_25",
                 lambda s: s["processors"] >= 75
                 and s["memory"] < 25
                 and btnAddMem.is_enabled(),
                 btnAddMem.click),
                ("raise_clip_price",
                 lambda s: s["clip_price"] < 0.13,
                 raise_clip_price.click),
                ("increase_marketing_10",
                 lambda s: s["marketing_level"] < 10 and btnMarketing.is_enabled(),
                 btnMarketing.click),
                ("increase_megaclippers",
                 lambda s: s["megaclippers"] < 15
                 and btnMakeMegaClipper.is_enabled(),
                 btnMakeMegaClipper.click),
                ("Increase_investment_level_8",
                 lambda s: s["invst_lvl"] < 8 and btnImproveInvestments.is_enabled(),
                 btnImproveInvestments.click),
                ("increase_marketing_8",
                 lambda s: s["marketing_level"] < 8 and btnMarketing.is_enabled(),
                 btnMarketing.click),
                ("Set_risk_high_after_lvl_6",
                 lambda s: s["invst_lvl"] >= 6
                 and s["invst_risk"] != "hi",
                 lambda: page.locator("#investStrat").select_option("hi")),
                ("invest_for_monopoly",
                 lambda s: s["megaclippers"] >= 15 
                 and s["marketing_level"] >= 8
                 and s["funds"] >= 5000
                 and s["wire"] >= 1000,
                 btnInvest.click),
            ],
            # P38 Full Monopoly
            "projects": [29, 38],
        },
        {
            "name": "Monopoly",
            "exit": lambda s: s["console1"] == "Full market monopoly achieved, public demand increased x10",
            "rules": [
                ("qcompute",
                 lambda s: s["qchip_value"] > 0.1,
                 lambda: rapid_click(page, "btnQcompute", 500)),
                ("new_tournament",
                 lambda s: btnNewTournament.is_enabled(),
                 btnNewTournament.click),
                ("run_tournament",
                 lambda s: btnRunTournament.is_enabled(),
                 btnRunTournament.click),
                ("add_processors_to_75",
                 lambda s: s["processors"] < 75 and btnAddProc.is_enabled(),
                btnAddProc.click),
                ("add_memory_to_25",
                 lambda s: s["processors"] >= 75
                 and s["memory"] < 25
                 and btnAddMem.is_enabled(),
                 btnAddMem.click),
                ("Shift_funds_to_achieve_monopoly",
                 lambda s: s["funds"] < 10_000_000
                 and btnWithdraw.is_enabled(),
                 btnWithdraw.click),
            ],
            # P38 Full Monopoly
            "projects": [29, 38],
        },
        {
            "name": "Reach 101M clips",
            "exit": lambda s: s["clips"] >= 101_000_000,
            "rules": [
                ("qcompute",
                 lambda s: s["qchip_value"] > 0.1,
                 lambda: rapid_click(page, "btnQcompute", 500)),
                ("new_tournament",
                 lambda s: btnNewTournament.is_enabled(),
                 btnNewTournament.click),
                ("run_tournament",
                 lambda s: btnRunTournament.is_enabled(),
                 btnRunTournament.click),
                ("add_processors_to_75",
                 lambda s: s["processors"] < 75 and btnAddProc.is_enabled(),
                btnAddProc.click),
                ("add_memory_to_25",
                 lambda s: s["processors"] >= 75
                 and s["memory"] < 25
                 and btnAddMem.is_enabled(),
                 btnAddMem.click),
                ("raise_clip_price",
                 lambda s: s["clip_price"] < 0.41,
                 raise_clip_price.click),
                ("increase_megaclippers",
                 lambda s: s["megaclippers"] < 93
                 and btnMakeMegaClipper.is_enabled(),
                 btnMakeMegaClipper.click),
                ("increase_marketing_15",
                 lambda s: s["marketing_level"] < 14 and btnMarketing.is_enabled(),
                 btnMarketing.click),
                ("lowbalance_risk_to_high",
                 lambda s: s["invst_lvl"] >= 6
                 and s["invst_risk"] != "hi",
                 lambda: page.locator("#investStrat").select_option("hi")),
                ("Increase_investment_level_9",
                 lambda s: s["invst_lvl"] < 9 and btnImproveInvestments.is_enabled(),
                 btnImproveInvestments.click),
                ("invest_for_300M",
                 lambda s: s["megaclippers"] >= 93
                 and s["port_value"] < 400_000_000
                 and s["marketing_level"] >= 14
                 and s["funds"] >= 50_000
                 and s["wire"] >= 1000,
                 btnInvest.click),
                ("boost_megaclippers_until_101M_clips",
                 lambda s: s["port_value"] >= 400_000_000
                 and btnMakeMegaClipper.is_enabled(),
                 btnMakeMegaClipper.click),
            ],
            # P10b Quantum foam anealment (16k wire spools)
            "projects": ["10b"],
        },
        {
            "name": "Reach 100 Trust for Hypnodrones",
            "exit": lambda s: s["releasedHypnoDrones"] == 1,
            "rules": [
                ("qcompute",
                 lambda s: s["qchip_value"] > 0.1,
                 lambda: rapid_click(page, "btnQcompute", 500)),
                ("new_tournament",
                 lambda s: btnNewTournament.is_enabled(),
                 btnNewTournament.click),
                ("run_tournament",
                 lambda s: btnRunTournament.is_enabled(),
                 btnRunTournament.click),
                ("add_processors_to_75",
                 lambda s: s["processors"] < 75 and btnAddProc.is_enabled(),
                btnAddProc.click),
                ("add_memory_to_25",
                 lambda s: s["processors"] >= 75 
                 and s["memory"] < 25
                 and btnAddMem.is_enabled(),
                 btnAddMem.click),
                ("Set_risk_low_once_funded",
                 lambda s: s["port_value"] >= 256_000_000
                 and s["invst_risk"] != "low",
                 lambda: page.locator("#investStrat").select_option("low")),
                ("sell_down",
                 lambda s: s["port_value"] >= 1_000,
                 btnWithdraw.click),
            ],
            # P40,40b Bribes to 100T
            # P35 Release the HypnoDrones
            "projects": ["40", "40b", "35"],
        },
    ]

    return stages

def save_json(page):
    # Extract the localStorage values
    page.evaluate("save1()")
    time.sleep(0.1)
    state = page.evaluate("""
        () => ({
            saveGame1: localStorage.getItem("saveGame1"),
            saveProjectsUses1: localStorage.getItem("saveProjectsUses1"),
            saveProjectsFlags1: localStorage.getItem("saveProjectsFlags1"),
            saveProjectsActive1: localStorage.getItem("saveProjectsActive1"),
            saveStratsActive1: localStorage.getItem("saveStratsActive1")
        })
    """)

    with open(save_file, "w") as f:
        json.dump(state, f, indent=2)

    print(f"saved game to {save_file}")

def load_json(page):
    # Restore localStorage
    with open(save_file) as f:
        state = json.load(f)

    page.evaluate("""
        (state) => {
            localStorage.setItem("saveGame1", state.saveGame1);
            localStorage.setItem("saveProjectsUses1", state.saveProjectsUses1);
            localStorage.setItem("saveProjectsFlags1", state.saveProjectsFlags1);
            localStorage.setItem("saveProjectsActive1", state.saveProjectsActive1);
            localStorage.setItem("saveStratsActive1", state.saveStratsActive1);
        }
    """, state)

    # Load dropdown values from the saved game state
    game = json.loads(state["saveGame1"])

    risk_index = {7: "low", 5: "med", 1: "hi"}
    risk_value = risk_index.get(game["riskiness"], "low") 
    strat_value = game["pick"]

    time.sleep(0.1)
    page.reload()
    time.sleep(0.1)
    page.evaluate("load1()")
    page.locator("#investStrat").select_option(risk_value)
    page.locator("#stratPicker").select_option(strat_value)

def run_stage(page, stage, stats):
    while not stage["exit"](stats):
        tick = stage.get("tick")
        if tick:
            tick()

        time.sleep(0.001)
        stats = read_values(page)

        for name, condition, action in stage["rules"]:
            if condition(stats):
                action()

        projects = stage.get("projects")
        if projects:
            click_projects(page, projects)

    return stats

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.decisionproblem.com/paperclips/index2.html")

        stats = read_values(page)
        print(stats["console1"])

        # LOAD savepoint
        # load_json(page)

        start_stage = 0
        save_stage = None #None to not save

        stages = list(make_stages(page))

        with Progress(
            TextColumn("[bold blue]{task.fields[stage]}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            ) as progress:
            task = progress.add_task("Running stages...", total=len(stages), stage="Starting...")

            for i, stage in enumerate(stages):
                progress.update(task, stage=f"Stage {i}: {stage['name']}")

                if i == save_stage:
                    save_json(page)
                if i >= start_stage:
                    print(f"-- {i} {stage['name']} --")
                    stats = run_stage(page, stage, stats)
                
                progress.advance(task)

        stats = read_values(page)
        print(stats)

        elapsed_time = time.perf_counter() - start_time
        print(f"Elapsed time: {format_time(elapsed_time)}")

        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()
