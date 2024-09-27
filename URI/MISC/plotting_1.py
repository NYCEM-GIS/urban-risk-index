""" make plots for distribution, and notebooks"""
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import URI.MISC.utils_1 as utils
from URI.PARAMS.params import PARAMS 
import URI.PARAMS.path_names as PATHNAMES
utils.set_home()
make_plots = PARAMS['make_plots'].value

bool_save = 1

#%% define for plotting
def plot_score(gdf, column, title, legend, cmap):
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)
    plt.axis('off')
    gdf.plot(ax=ax, column=column, legend=True, cmap=cmap, categorical=True,
                  legend_kwds={'title': 'Score', 'bbox_to_anchor':(.2, .9),
                               'frameon':False})
    gdf.boundary.plot(ax=ax, color='k', lw=0.1)
    plt.title(title, fontsize=20)
    plt.show()
    pass

#%%%
def plot_raw(gdf, column, title, legend, cmap):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    plt.title(title, fontsize=20)
    plt.axis('off')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=1.0)
    gdf.plot(ax=ax, column=column, legend=True, cmap=cmap, categorical=False, cax=cax,
                    legend_kwds={'label': legend})
    gdf.boundary.plot(ax=ax, color='k', lw=0.1)
    pass

#%%
def plot_notebook(gdf, column, title, legend, cmap, type='score'):
    if make_plots:
        if type=='score':
            plot_score(gdf, column, title, legend, cmap)
            plt.show()
            pass
        elif type=='raw':
            plot_raw(gdf, column, title, legend, cmap)
            plt.show()
            pass
        else:
            pass
    else:
        pass

#%%
def plot_inline(gdf_data, column, scheme='equal_interval'):
    fig = plt.figure(figsize=(9, 6.5))
    ax = fig.add_subplot(111)
    if scheme=='equal_interval':
        gdf_data.plot(ax=ax, column=column, categorical=False, legend=True)
    else:
        gdf_data.plot(ax=ax, column=column, categorical=False, legend=True,
                      scheme=scheme)
    plt.show()

#%%
if __name__ == '__main__':

    gdf = utils.get_blank_tract()
    plot_notebook(gdf, column='Acres', title = 'Title', legend = 'Legend', cmap='Blues', type='raw')

