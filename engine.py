from typing import Tuple, List
from map import Map
from agent import Agent, Curiosity, Linear, Random, Motivation
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import csv

# TODO: Might want to make more efficient so that graphing doesn't take so long


def plot_paths(map: Map, agent_lst: List[Agent], show: bool, save: bool, dirname: str):
    """Plots out the paths of the agents on the map
    
    Params
    ------
    map: Map
        A map that will be used to get the bounds and background for plotting
    
    agent_lst: List[Agent]
        A list of agents whose paths need to be plotted
    
    show: bool
        Whether the plots should be displayed or not
    
    save: bool=False
        Whether the graphs should be saved

    dirname: str
        The directory where the images will be stored

    Returns
    -------
    None
    """

    # Doesn't spend the time making the charts unless the user wants it
    if(show or save):
        # Create one large image with all agents at once

        # Gets the x,y limits of the image so the graph can be sized accordingly
        x_lim = [0, map.img.size[1]]
        y_lim = [0, map.img.size[0]]

        # Set up the plot
        fig, ax = plt.subplots(facecolor='w', figsize=(8, 3.5), dpi=130)
        # Chow the image in greyscale
        ax.imshow(map.img, extent=y_lim+x_lim, cmap='Greys_r')
        # Since the origin is at the top left, we're going to invert the y axis
        ax.invert_yaxis()

        # Cycle through every agent, put their x,y coordinates into separate lists,
        # and then plot them
        for agent in agent_lst:
            # Splits x and y into separate lists (technically tuples)
            x, y = zip(*agent.history)
            print(x, "\n\n\n")
            # Plot those points on the graph. The lines are transparent because
            # sometimes the agents cross over each other and you still want to
            # see the paths of those underneath
            ax.plot(x, y, label=agent, alpha=0.5)

        # Annotate the chart
        ax.set_title("Combined Agent Paths")
        # Place the legend outside of the chart since we never know where the
        # agents are going to go
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Legend')
        # Fix the alignment of the image on export
        ax.set_position([0.1, 0, 0.5, 1.0])

        # Save the image if they want it
        # NOTE: I chose svg because it retains its high wuality while being a relatively small file
        if(save):
            plt.savefig("{}/all.svg".format(dirname))

        # Show it if they want it
        # NOTE: this has to be done in this order or it will save blank images
        if(show):
            plt.show()

        # Create multiple plots with one agent each

        for agent in agent_lst:
            # Create a plot, same as before but shaped a little differently because
            # we don't have the legend
            fig, ax = plt.subplots(facecolor='w', figsize=(8, 4.5), dpi=80)
            # plot the image
            ax.imshow(map.img, extent=y_lim+x_lim, cmap='Greys_r')
            ax.invert_yaxis()

            # Put the x and y values in two sepearate lists
            x, y = zip(*agent.history)
            # Plot the agents. The color is arbitrary but I thought it stood out well.
            # These plots have transparencies as well to stay consistent with the others
            ax.plot(x, y, alpha=0.5, c="orange")

            for x,y in agent.history:
                rect = patches.Rectangle((x-32, y-32), 64, 64, linewidth=1, edgecolor='r', facecolor='none', alpha=0.1)
                ax.add_patch(rect)

            # Name the plot after the agent
            ax.set_title(agent)

            # Save the image if desired
            if(save):
                # get rid of all of the characters we don't want in a fipe path
                filename = str(agent).replace(" ", "_").replace(
                    "(", "").replace(")", "").replace(",", "_")
                # Save the file
                plt.savefig("{}/{}.svg".format(dirname, filename))

            # Show the image if desired
            if(show):
                plt.show()


def run_experiment(motivation_lst: List[Motivation], position_lst: List[Tuple[int]], map: Map, iterations: int, show: bool = True, saveGraph: bool = False, saveLocation: bool = True, dirname: str = None):
    """Runs an experiment on the motication given, then handles plotting and saving data. Agents are updated in a round-robin configuration, so each gets an ewual number of executions, and they all rpogress together.
    
    Params
    ------
    motivation_lst: List[Motivation]
        A list of Motivation class instances to be used as the drivers for agents. This must be the same length as position_lst

    position_lst: List[Tuple[int]]
        A list of poitions for the agents to start out at (matching indices with elements from motivation_lst). It must be the same length as potivation_lst.
    
    map: Map
        An instance of the Map class that will be used by the agent to handle directions, and for the plotting
    
    iterations: int
        The number of steps that each agent should take.

    show: bool=True
        Whether the graphs should be displayed

    saveGraph: bool
        Whether the plots should be saved to the disk or not

    saveLoction: bool
        Whether the agent's position should be save to the disk

    dirname: str=None
        The directory in which the graphs will be stored

    
    Returns
    -------
    None

    """

    # Make sure that the parameters are valid
    assert len(motivation_lst) == len(position_lst)
    assert (saveGraph == False and saveLocation == False) or dirname is not None

    agent_lst = []

    # Generate a bunch of agents from the motivation, positions, and map
    for motiv, pos in zip(motivation_lst, position_lst):
        agent_lst.append(Agent(motiv, pos))

    progress_bar_width = 50
    num_agents = len(agent_lst)
    current_agent_id = 1
    
    for agent in agent_lst:
        for i in range(iterations):
            # Error handling in case something goes wrong
            try:
                agent.step()
            except Exception as e:
                # TODO: Should probably replace this with a stack trace
                print('Problem at step ', i, " with agent:", agent)
                print(e)
                return
        
            # Update progress bar for agent
            frac = (i+1) / float(iterations)
            left = int(progress_bar_width * frac)
            right = progress_bar_width - left
            print(f'\rAgent {current_agent_id}/{num_agents} Experiment Progress [', '#' * left, ' ' * right, ']', f' {frac*100:.0f}% ', sep='', end='', flush=True)
        print("") # Moves carriage to next line
        current_agent_id += 1

    # Graph the agent's paths
    plot_paths(map, agent_lst, show, saveGraph, dirname)

    save_agent_data(agent_lst, saveLocation, dirname)


def save_agent_data(agent_lst: List[Agent], save: bool, dirname: str):
    """
    Save the path record of each agent as a csv file
    
    Params:
    ------
    agent_lst: List[Agent]
        A list of agent whose path coordinates to be saved
    
    save: bool
        Save the agent's path data or not
    
    dirname: str
        THe directory name where the csv file will be saved

    Returns:
    ------
    None
    """

    # Iterates over all of the agents
    for agent in agent_lst:
        if save:
            fields = ['x', 'y']
            # Change the Agent's name into a valid filename
            filename = str(agent).replace(" ", "_").replace(
                "(", "").replace(")", "").replace(",", "_") + '_path_record'

            # Save the coordinates to a file
            with open(dirname + '/' + filename + '.csv', 'w', newline='') as f:
                wr = csv.writer(f)
                wr.writerow(fields)
                wr.writerows(agent.history)


def load_agent_data(path: str):
    """
    Loads information from a given file. This will not be used as part of the engine.
    However, I thought it would be useful to include here so that if we make changes to
    the serialization, we have the data loding close by and can edit it easily

    Params
    ------

    path: str
        The path to the file

    Returns
    -------

    List[Tuple[int]]
        Returns a list of x and y coordinates

    """

    # Makes sure that the path is given and that the file is a csv file
    assert path != None and path.split(".")[-1] == "csv"

    # Create a list to hold the coordinates as they're read from the file
    lst_content = []

    # Open the csv file
    with open(path, 'r', newline='') as agent_p_file:
        # Create a csv reader to read the information out of it
        csv_reader = csv.reader(agent_p_file, delimiter=',')
        # Iterate through all rows
        for row in csv_reader:
            # Add each row of data to our list of points
            lst_content.append(row)

    # Changing the rows from lists of strings to tuples of ints
    # (and also removing the headers)
    return list(map(lambda x: tuple(map(int, x)), lst_content[1:]))

if __name__ == "__main__":
    from memory import PriorityBasedMemory, ListBasedMemory
    from brain import Brain
    fov = 64 # Allowed FOVs = {32, 64, 128}
    map = Map('data/mars.png', fov, 2)

    brain = Brain(PriorityBasedMemory(64), (fov,fov,1), nov_thresh=0.25, novelty_loss_type='MSE', train_epochs_per_iter=1)
    motivations = [Random(map=map), Linear(map=map)] # Curiosity(map=map, brain=brain)]
    positions = [(2000,1000), (2000, 1000)] # (2000, 1000)]
    run_experiment(motivations, positions, map, 1000, saveLocation=True, saveGraph=True, show=False, dirname="./output_dir")