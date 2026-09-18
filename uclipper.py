# ---------------------------------------------------------------------
# UClipper - Playwright Speed Run designer for Universal Paperclips
# www.decisionproblem.com/paperclips/
# ---------------------------------------------------------------------

from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from playwright.sync_api import sync_playwright
from pathlib import Path
import operator
import json
import time
import yaml
import re

save_dir = Path("uclipper_saves")
save_dir.mkdir(exist_ok=True)

start_time = time.perf_counter()

log = []
milestones = [
    "clips created",
    "Quantum computing online",
    "Full autonomy attained",
    "Clips Created",
    "Terrestrial resources fully utilized",
    "Von Neumann Probes online"
]

def format_time(seconds):
    """Format time in seconds to MM:SS"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def load_stages_config(filename="stages.yaml"):
    """Load stages configuration from a YAML file."""
    with open(filename, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config["stages"]

def get_button_id(button_name):
    button_mapping = {
        "make_paperclip": "#btnMakePaperclip",
        "raise_clip_price": "#btnRaisePrice",
        "lower_clip_price": "#btnLowerPrice",
        "buy_wire": "#btnBuyWire",
        "add_processors": "#btnAddProc",
        "add_memory": "#btnAddMem",
        "qcompute": "#btnQcompute",
        "marketing": "#btnExpandMarketing",
        "make_clipper": "#btnMakeClipper",
        "make_mega_clipper": "#btnMakeMegaClipper",
        "wire_buyer": "#btnToggleWireBuyer",
        "invest": "#btnInvest",
        "withdraw": "#btnWithdraw",
        "new_tournament": "#btnNewTournament",
        "run_tournament": "#btnRunTournament",
        "improve_investments": "#btnImproveInvestments",
        "add_factory": "#btnMakeFactory",
        "add_harvester": "#btnMakeHarvester",
        "add_wire_drone": "#btnMakeWireDrone",
        "add_farm": "#btnMakeFarm",
        "add_battery": "#btnMakeBattery",
        "add_farm10": "#btnFarmx10",
        "add_harvester100": "#btnHarvesterx100",
        "add_wire_drone100": "#btnWireDronex100"
    }

    return button_mapping.get(button_name, None)

def compare(actual, op_string, expected):
    """Custom helper function to map string operators to Python logic."""
    # Define the mapping of strings to operator functions
    ops = {
        ">": operator.gt,
        ">=": operator.ge,
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        "in": lambda a, b: a in b,  # Custom handling for 'in' checking
    }

    # Fetch the function from the dictionary
    op_func = ops.get(op_string)

    if not op_func:
        raise ValueError(f"Unsupported operator: {op_string}")

    # Execute the comparison
    return op_func(actual, expected)

def check_condition(page, condition, stats):
    """Recursively check conditions based on the provided structure."""
    if "all" in condition:
        return all(
            check_condition(page, c, stats)
            for c in condition["all"]
        )

    if "any" in condition:
        return any(
            check_condition(page, c, stats)
            for c in condition["any"]
        )

    if any(key in condition for key in ["stat", "value_stat"]):
        actual = stats[condition["stat"]]
        operator = condition["operator"]

        if "value_stat" in condition:
            expected = stats[condition["value_stat"]]
        else:
            expected = condition["value"]

        return compare(actual, operator, expected)

    if "button" in condition:
        button_id = get_button_id(condition["button"])
        locator = page.locator(button_id)

        if condition["state"] == "enabled":
            return locator.is_enabled()

        if condition["state"] == "visible":
            return locator.is_visible()

    return False

def execute_action(page, action):
    """Execute an action based on the provided structure."""
    action_type = action["type"]

    if action_type == "click":
        button_id = get_button_id(action["button"])
        locator = page.locator(button_id)
        locator.click()

    elif action_type == "rapid_click":
        button_id = get_button_id(action["button"]).lstrip("#")
        rapid_click(page, button_id, action["clicks"])

    elif action_type == "select":
        if action["element"] == "strategy":
            page.locator("#stratPicker").select_option(action["value"])
        elif action["element"] == "investment_strategy":
            page.locator("#investStrat").select_option(action["value"])


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

            factoryLevel: factoryLevel,
            harvesterLevel: harvesterLevel,
            wireDroneLevel: wireDroneLevel,
            farmLevel: farmLevel,
            batteryLevel: batteryLevel,
            batterySize: batterySize,

            pwr_consumption: (harvesterLevel + wireDroneLevel) + (factoryLevel * 200),
            pwr_production: farmLevel * 50,

            //flags
            creativityOn: creativityOn,
            wireBuyerStatus: wireBuyerStatus,
            strategyEngineFlag: strategyEngineFlag,
            investmentEngineFlag: investmentEngineFlag,
            releasedHypnoDrones: project35.flag,
            momentumFlag: project125.flag,
            spaceExplorationFlag: project46.flag
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


def rapid_click(page, button_id, clicks):
    page.evaluate(
        """
        ({ buttonId, clicks }) => {
            const button = document.getElementById(buttonId);
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


def save_json(page, stage_index, stage_name):
    # Save game state and uclipper stage to json
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
    
    # Save the stage information alongside the game state
    state["stage_index"] = stage_index
    state["stage_name"] = stage_name

    save_file = save_dir / f"stage_{stage_index:02d}.json"

    with open(save_file, "w") as f:
        json.dump(state, f, indent=2)

    print(f"saved game to {save_file}")

def get_last_stage():
    pattern = re.compile(r"^stage_(\d+)\.json$")
    
    valid_stages = []
    for file in save_dir.glob("stage_*.json"):
        match = pattern.match(file.name)
        if match:
            stage_num = int(match.group(1))
            # Store as a tuple: (integer_number, filename)
            valid_stages.append((stage_num, file.name))
            
    if not valid_stages:
        return None
    
    _, highest_filename = max(valid_stages)
    return highest_filename

def load_json(page):
    # Load game state and uclipper stage from json
    filename = get_last_stage()
    if filename:
        save_file = save_dir / filename

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

    start_stage = state.get("stage_index", 0)

    # Load dropdown values from the saved game state
    game = json.loads(state["saveGame1"])

    risk_index = {7: "low", 5: "med", 1: "hi"}
    risk_value = risk_index.get(game["riskiness"], "low") 
    strat_value = game["pick"]

    time.sleep(0.1)
    page.reload()
    time.sleep(0.1)
    page.evaluate("load1()")
    if page.locator("#investStrat").is_visible():
        page.locator("#investStrat").select_option(risk_value)
    if page.locator("#stratPicker").is_visible():
        page.locator("#stratPicker").select_option(strat_value)

    return start_stage

def run_stage(page, stage, stats):
    while not check_condition(page, stage["exit"], stats):
        tick = stage.get("tick")
        if tick:
            execute_action(page, tick)
            stats = read_values(page)
        
        for rule in stage["rules"]:
            if check_condition(page, rule["condition"], stats):
                execute_action(page, rule["action"])

        click_projects(page, stage.get("projects", []))
        stats = read_values(page)

    return stats


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.decisionproblem.com/paperclips/index2.html")

        stats = read_values(page)
        print(stats["console1"])

        # LOAD savepoint
        start_stage = load_json(page)
        save_stage = None #None to not save

        # stages = list(make_stages(page))
        stages = load_stages_config()

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
                    save_json(page, i, stage['name'])
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
