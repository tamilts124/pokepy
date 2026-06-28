"""Replace all creature desc one-liners with richer 2-3 sentence lore blurbs."""
import pathlib, re

LORE = {
    "Flambit":    "A tiny lizard whose tail blazes with a flame that mirrors its emotions. Brave and energetic, it rushes into fights before thinking twice. Trainers say its tail flares brightest in the heat of battle.",
    "Flamclaw":   "Its curved claws burn red-hot during combat, searing whatever they rake across. The heat is so intense that raindrops hiss to steam the moment they touch its body. Rival trainers dread facing one in close quarters.",
    "Infernox":   "A fearsome creature of living flame, shaped like a towering dragon wrapped in fire. Ancient texts call it the Infernal Sovereign — a beast whose roar has been known to ignite forests from a kilometre away. Only the most seasoned trainers dare to challenge one.",
    "Leafling":   "A small plant creature bursting with curiosity and wanderlust, always poking its vines into places they don't belong. The leaves on its back absorb sunlight constantly, giving it a wellspring of gentle energy. It smells faintly of fresh rain.",
    "Thornbush":  "Its thorns are tipped with a paralysing sap that it shakes loose when threatened. The vines running along its arms have grown thick and ropey, strong enough to uproot small trees. Rival creatures learn to keep their distance.",
    "Goliavine":  "A towering jungle guardian wreathed in dense vines and oversized leaves that block out the sun. Village elders claim that forests grow back overnight wherever a Goliavine has slept. Its presence is said to drive off poachers and predators alike.",
    "Aquapup":    "A cheerful water pup that splashes anything within reach just to see the ripples. Its round, rubbery body makes it nearly impossible to hold onto once it gets wet. Coastal villages keep them around for their uncanny ability to find underground springs.",
    "Tidalfin":   "Evolved fins let it cut through water faster than the eye can follow, leaving a glittering wake of bubbles. It spends most of its time at river mouths, leaping clear out of the water to snatch insects mid-flight. Sailors consider it a good omen.",
    "Abyssking":  "Ruler of the deep ocean, it dives to crushing depths where no light reaches and the pressure would flatten a boulder. Its roar echoes through submarine canyons and sends entire schools of fish fleeing for the shallows. No creature disputes its authority beneath the waves.",
    "Buzzbee":    "A common bug found in tall grass, small enough to overlook but persistent enough to annoy. Its tiny stinger can deliver a mild toxin that causes numbness for an hour. Farmers tolerate them because they also pollinate crops while wandering.",
    "Hornwing":   "Its wings beat at a frequency that produces a low, irritating hum audible from thirty metres away. The hardened horn on its head is used to bore through rotting wood in search of grubs. Despite its aggressive reputation, it rarely attacks unless its nest is threatened.",
    "Pebblur":    "A rolling rock creature that tucks itself into a perfect sphere and bowls over anything in its path. Young ones are barely distinguishable from ordinary pebbles until they blink. Geologists sometimes accidentally carry them home in sample bags.",
    "Bouldrax":   "Its granite-hard body can shrug off pickaxe blows without so much as a scratch. It communicates with others of its kind by striking the ground with a rhythmic thud that carries for kilometres underground. Quarry workers in Stonepeak say the tremors from their arguments register on seismographs.",
    "Sparkit":    "Sparks shower from its cheeks whenever it feels a strong emotion, which is frequently. During storms it climbs to high ground, raises its tail like a lightning rod, and seems to enjoy every bolt that strikes it. Children dare each other to pet one.",
    "Voltfang":   "A lightning beast whose fangs crackle with stored static — the bite doesn't just hurt, it numbs. Its Intimidate ability causes nearby creatures to reflexively lower their guard before the battle even begins. Championship trainers prize it for its terrifying combination of speed and raw power.",
    "Ghostlet":   "Floats silently through walls and closed doors, peering at sleeping trainers with wide, curious eyes. It can't help itself — it's simply fascinated by the living. The cold spots it leaves behind linger for hours.",
    "Spectrex":   "Its haunting gaze can lock up an opponent's nervous system before a single blow is thrown. The psychic energy it absorbed after evolving gives its attacks a spectral quality that unsettles even hardened opponents. Ghost-type trainers in Shadowmere consider it their signature creature.",
    "Iceling":    "Leaves a thin trail of frost wherever it treads, and the grass beneath its paws doesn't thaw until noon. In Frostholm, children track them by following the icy footprints across the cobblestones each morning. It is gentle by nature and rarely picks fights.",
    "Glacivore":  "A mighty ice beast of the tundra, capable of surviving blizzards that would bury entire cabins overnight. Its thick fur traps a layer of super-cooled air against its skin, insulating it from even the sharpest electric attacks. Elder Blizara keeps one as a personal guardian.",
    "Drakling":   "A small dragon with untapped potential, all gangly limbs and oversized wings it hasn't grown into yet. It scorches the grass practicing Dragon Breath and never quite manages to land. What it lacks in power it makes up for in stubbornness.",
    "Drakonis":   "A proud dragon feared by many in the mountain passes, its scales now dense enough to deflect arrows. It circles high on thermals for hours, surveying its territory before diving with terrifying speed. Trainers who earn its loyalty are rarely challenged twice.",
    "Wyrmax":     "The apex dragon, feared across the continent and revered in equal measure. Its roar alone has been known to split cliff faces and send avalanches cascading down mountainsides. Legends say that a trainer who tames a Wyrmax inherits its destiny.",
    "Steelbit":   "A metallic creature whose shell is its most prized possession — it polishes it obsessively with its tongue. Despite its stubborn, cautious exterior, it forms deep bonds with patient trainers who earn its trust. Its Sturdy ability means it refuses to be knocked out in a single hit.",
    "Ironclaw":   "Its claws can tear through solid rock with the casual ease of clipping a fingernail. Once it locks its grip on an opponent, no amount of struggling dislodges it — trainers have timed the hold at over four minutes. The mine shafts under Stonepeak are riddled with its claw marks.",
    "Mudpup":     "Loves nothing more than diving headfirst into murky swamp water and emerging coated head to toe in fragrant mud. Its flat, paddle-like tail generates surprising currents underwater, letting it surf slow rivers without moving a limb. Fishermen in Marshfen find them tangled in their nets more often than actual fish.",
    "Sludgedon":  "A massive swamp beast of immense strength, capable of dragging river barges off sandbars with a single shrug. Its body is part mud, part water, and always warm from the decomposing organic material it wallows in. Locals say the wetland is healthiest where a Sludgedon has claimed territory.",
    "Skywing":    "Soars high above the clouds on rising thermals, sometimes for days at a time without landing. Its hollow bones are lighter than balsa wood, and even a strong gust can carry it dozens of kilometres off course. Fledglings are notoriously easy to lose on windy days.",
    "Stormcrest": "Rides thunderclouds like a living conductor, absorbing lightning and redirecting it through its wings. The boom of its Speed Boost-accelerated dive sounds exactly like a thunderclap, which it uses for ambush. Stormwatchers in Mistveil claim sightings always precede three days of bad weather.",
    "Venomfang":  "Its hollow fangs drip with a paralytic venom potent enough to stop a horse mid-stride. It hunts by tracking body heat through dense foliage, striking before its prey even registers movement. The antidote for its bite is expensive and hard to find outside major towns.",
    "Toxidra":    "A venomous serpent that lurks in the dark places between walls and under floorboards, waiting for an opportunity. The dark energy it absorbed after evolving added a psychological edge: victims report feeling watched long after the creature has slunk away. Shadowmere's shadow-cult consider it sacred.",
    "Psychling":  "Can read surface thoughts but is physically frail — it relies entirely on confusion and mental pressure to avoid direct blows. It dislikes crowded places because the noise of a hundred minds at once gives it splitting headaches. Trainers with calm, focused minds are the only ones it trusts.",
    "Mindstrike": "The fastest creature alive, capable of launching a full attack sequence before most opponents register it has moved. It perceives the entire battlefield as slow motion, which is why it seems so effortlessly composed even in chaos. Researchers have never managed to photograph one in motion without blur.",
    "Mushrump":   "Releases clouds of fine sleep-inducing spores whenever it feels threatened, which is unfortunately very often. The spores settle in a rough half-metre radius and remain viable for up to six hours. Campers near the deep forest have woken with no memory of the night before.",
    "Fungolith":  "An ancient mushroom giant of the deep forest, so old that ferns and moss have taken root on its cap. Its massive bulk absorbs physical blows like a sponge — the Thick Fat ability is literal here, a dense layer of fatty tissue under the bark-like skin. Local legends say Fungolith sightings predict a bountiful harvest.",
    "Shellcrab":  "Hides inside its impenetrable shell at the first sign of danger, clamping shut with a force that no tool in any trainer's kit can pry open. It feeds on shellfish and small fish it scoops up with its claws at low tide. The clicking sound it makes when content echoes through sea caves.",
    "Tideshell":  "Its shell has been reinforced by centuries of saltwater, tidal pressure, and the strikes of countless challengers until it rivals cast iron. Geologists have confirmed that the calcium lattice in its shell is unlike any naturally occurring mineral. Even Iron Tail barely leaves a mark.",
    "Ashpup":     "Born from volcanic ash, its body is always warm to the touch — even in a blizzard, its fur is never cold. It plays in lava flows the way other creatures play in puddles, emerging covered in cooling rock that it shakes off like mud. Miners keep them around mine entrances as living heat sensors.",
    "Volcanix":   "A volcanic hound that erupts in battle, venting superheated gas from vents along its spine when its Blaze ability triggers. The ground beneath its feet cracks and scorches with every heavy step. Volcanologists claim that the tremors around Ashveil always intensify when wild Volcanix are active nearby.",
}

path = pathlib.Path('data/creatures.py')
src = path.read_text(encoding='utf-8')

for name, lore in LORE.items():
    # Each creature desc is on a line like:
    #   "desc": "old text",
    # We match that specific line's value (old one-liner) and replace with new text.
    # Use a regex that's anchored to the key name earlier on the same line
    old_pattern = rf'("desc": ")[^"]*(")'
    # But we only want to replace within the block for THIS creature name.
    # Strategy: split on creature name header, replace only the first desc in that block.
    # Find the creature's section start and replace only the next "desc" occurrence.
    marker = f'"{name}":'
    idx = src.find(marker)
    if idx == -1:
        print(f"WARNING: creature {name!r} not found in source")
        continue
    # Find next "desc": after this position
    desc_idx = src.find('"desc":', idx)
    if desc_idx == -1:
        print(f"WARNING: no desc field for {name!r}")
        continue
    # Find the value start and end (between the quotes)
    val_start = src.index('"', desc_idx + 7) + 1  # after "desc": "
    val_end   = src.index('"', val_start)
    old_val = src[val_start:val_end]
    # Replace only this instance
    src = src[:val_start] + lore + src[val_end:]
    print(f"  OK: {name:<14} {old_val[:40]!r} -> {lore[:40]!r}")

path.write_text(src, encoding='utf-8')
print(f"\nWrote {path} ({len(src)} bytes)")
