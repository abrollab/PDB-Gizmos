change

# Example JSON file that may serve as the default input file.
```json
{
    "name": "SeedPicker.in",
    "Topology" : "path/to/topology/file.prmtop",
    "groups" : {
        "Inactive" : {
            "trajs" : ["path/to/traj1.nc","path/to/traj2.nc","path/to/traj3.nc"],
            "crystal" : "3eml.pdb"
        },
        "Intermediate" : {
            "trajs" : ["path/to/traj4.nc","path/to/traj6.nc","path/to/traj9.nc"],
            "crystal" : "4ug2.pdb"
        },
        "active" : {
            "trajs" : ["path/to/traj19.nc","path/to/traj10.nc","path/to/traj11.nc"],
            "crystal" : "path/to/traj19.nc"
        }
    }
}
```
