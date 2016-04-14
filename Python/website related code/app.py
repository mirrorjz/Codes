"""
This is part of the code that implements the interactive recommendation website I built for "Locating the best
retirement home"


https://diijing.herokuapp.com
"""

from flask import Flask, render_template, request, redirect
import random

# imports for Bokeh plotting
from bokeh.plotting import figure
from bokeh.io import output_file, show, vplot, gridplot, hplot
from bokeh.embed import file_html, components
import pandas as pd
import numpy as np
import math
from pandas import DataFrame

# from scipy.ndimage.filters import uniform_filter
import densitymap as dm

#TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,tap,previewsave,box_select,poly_select,lasso_select"
TOOLS="resize,pan,wheel_zoom,box_zoom,reset,tap,previewsave,box_select,poly_select,lasso_select"

app = Flask(__name__)

app.vars={}
app.importance = []
app.rating_bar = []
app.review_count = []
app.distance = []

@app.route('/')
def main():
  return redirect('/index')
  
@app.route('/index',methods=['GET','POST'])
def index():
    
    if request.method == 'POST':
        return redirect(url_for('index'))
    
    return render_template('index_cover.html')

@app.route('/1')
def Plot1():
    # load data from static folder
    filename = 'static/data1.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['coord_x'].values)
    coord_y = list(df['coord_y'].values)
    radii = [x*0.1 for x in list(df['rating'].values)]
    colors = ["#%02x%02x%02x" % ((0.5-r)*500, r*500, 0) for r in radii]
    
    # create a new plot with default tools, using figure
    plot1 = figure(tools=TOOLS, title='#1: Doctor ratings in LA (green:high rating; red:low rating)', x_axis_label='X (km)', y_axis_label='Y (km)', x_range=(-10, 130), y_range=(-10, 90), plot_width=700, plot_height=500)
    plot1.scatter(coord_x, coord_y, legend="All doctors", radius=0.4, fill_color=colors, fill_alpha=0.5, line_color=None)
    
    plot1.quad(top=65, bottom=45, left=-5,
       right=18, legend="Hollywood", line_color="red", line_width=2, fill_color=None, fill_alpha=0.5)
    plot1.quad(top=25, bottom=5, left=45,
       right=70, legend="Orange County", line_color="blue", line_width=2, fill_color=None, fill_alpha=0.5)
    
    #script, div = components(plot)   
    #return render_template('graph.html', script=script, div=div)	
	
	
#@app.route('/2')
#def Plot2():
    # create a new plot with default tools, using figure
    plot2 = figure(tools=TOOLS, title='#2: Categorical ratings (bigger circle = higher rating)', x_axis_label='X (km)', y_axis_label='Y (km)', x_range=(-10, 130), y_range=(-10, 90), plot_width=700, plot_height=500)
    
    # load data from static folder
    
    filename = 'static/Family Practicestats.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['coord_x'].values)
    coord_y = list(df['coord_y'].values)
    radii = [x*0.1 for x in list(df['rating'].values)]
    #colors = ["#%02x%02x%02x" % (r*500, r*300, 150) for r in radii]
    plot2.scatter(coord_x, coord_y, legend="Family Practice", radius=radii, fill_color="blue", fill_alpha=0.1, line_color=None)
    
    filename = 'static/Cosmetic Surgeonsstats.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['coord_x'].values)
    coord_y = list(df['coord_y'].values)
    radii = [x*0.1 for x in list(df['rating'].values)]
    #colors = ["#%02x%02x%02x" % (r*500, r*300, 150) for r in radii]
    plot2.scatter(coord_x, coord_y, legend="Cosmetic", radius=radii, fill_color="yellow", fill_alpha=0.2, line_color=None)
    
    filename = 'static/Physical Therapystats.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['coord_x'].values)
    coord_y = list(df['coord_y'].values)
    radii = [x*0.1 for x in list(df['rating'].values)]
    #colors = ["#%02x%02x%02x" % (r*500, r*300, 150) for r in radii]
    plot2.scatter(coord_x, coord_y, legend="Phy. Therapy", radius=radii, fill_color="green", fill_alpha=0.2, line_color=None)
    
    filename = 'static/Urgent Carestats.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['coord_x'].values)
    coord_y = list(df['coord_y'].values)
    radii = [x*0.1 for x in list(df['rating'].values)]
    #colors = ["#%02x%02x%02x" % (r*500, r*300, 150) for r in radii]
    plot2.scatter(coord_x, coord_y, legend="Urgent Care", radius=radii, fill_color="red", fill_alpha=0.2, line_color=None)
    
    plot2.quad(top=65, bottom=45, left=-5,
       right=18, legend="Hollywood", line_color="red", line_width=2, fill_color=None, fill_alpha=0.5)
    plot2.quad(top=25, bottom=5, left=45,
       right=70, legend="Orange County", line_color="blue", line_width=2, fill_color=None, fill_alpha=0.5)
    plot2.quad(top=75, bottom=60, left=20,
       right=40, legend="Pasadena", line_color="orange", line_width=2, fill_color=None, fill_alpha=0.5)   
       
    plot = vplot(plot1, plot2)
    script, div = components(plot)   
    return render_template('graph_theme_v1.html', script=script, div=div)			

@app.route('/2')
def Plot2():
    # load data from static folder
    filename = 'static/data1_rb4.5_revc10_densitymap.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['g_x'].values)
    coord_y = list(df['g_y'].values)
    radii = [min(0.5, x*0.05) for x in list(df['count'].values)]
    colors = ["#%02x%02x%02x" % ((0.5-r)*500, r*500, 0) for r in radii]
    
    # create a new plot with default tools, using figure
    plot1 = figure(tools=TOOLS, title='All doctors (rating>=4.5, review>=10) (green:high; red:low)', x_axis_label='X (km)', y_axis_label='Y (km)', x_range=(-10, 130), y_range=(-10, 90), plot_width=700, plot_height=500)
    plot1.scatter(coord_x, coord_y, legend="All doctors", radius=0.4, fill_color=colors, fill_alpha=0.5, line_color=None)
    
    plot1.quad(top=65, bottom=45, left=-5,
       right=18, legend="Hollywood", line_color="red", line_width=2, fill_color=None, fill_alpha=0.5)
    plot1.quad(top=25, bottom=5, left=45,
       right=70, legend="Orange County", line_color="blue", line_width=2, fill_color=None, fill_alpha=0.5)
    plot1.quad(top=70, bottom=60, left=28,
       right=36, legend="Pasadena", line_color="orange", line_width=2, fill_color=None, fill_alpha=0.5)   
    #script, div = components(plot)   
    #return render_template('graph.html', script=script, div=div)				

#@app.route('/3')
#def Plot3():
    # load data from static folder
    filename = 'static/data1_rb0.0_revc0_densitymap.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['g_x'].values)
    coord_y = list(df['g_y'].values)
    radii = [min(0.5, x*0.05) for x in list(df['count'].values)]
    colors = ["#%02x%02x%02x" % ((0.5-r)*500, r*500, 0) for r in radii]
    
    # create a new plot with default tools, using figure
    plot2 = figure(tools=TOOLS, title='All doctors densitymap in LA (green:high; red:low)', x_axis_label='X (km)', y_axis_label='Y (km)', x_range=(-10, 130), y_range=(-10, 90), plot_width=700, plot_height=500)
    plot2.scatter(coord_x, coord_y, legend="All doctors", radius=0.4, fill_color=colors, fill_alpha=0.5, line_color=None)
    
    plot2.quad(top=65, bottom=45, left=-5,
       right=18, legend="Hollywood", line_color="red", line_width=2, fill_color=None, fill_alpha=0.5)
    plot2.quad(top=25, bottom=5, left=45,
       right=70, legend="Orange County", line_color="blue", line_width=2, fill_color=None, fill_alpha=0.5)
    
    plot = vplot(plot2, plot1)
    script, div = components(plot)   
    return render_template('graph3_theme.html', script=script, div=div)				


@app.route('/table1')
def show_table1():
    input_data = pd.read_csv('static/rec/example1.csv')
    #input_data.head(1).to_html(classes = 'User Inputs')
    input_data.columns = ['category', 'importance', 'rating bar', 'review number', 'distance']
    input_data.set_index(['category'], inplace=True)
    input_data.index.name=None
    # return render_template('view_theme.html', tables = [input_data.to_html(classes = 'Userinput')], titles = ['na', 'User Input #1'])
    
# @app.route('/table2')
# def show_table2():
    input_data_2 = pd.read_csv('static/rec/example2.csv')
    #input_data.head(1).to_html(classes = 'User Inputs')
    input_data_2.columns = ['category', 'importance', 'rating bar', 'review number', 'distance']
    input_data_2.set_index(['category'], inplace=True)
    input_data_2.index.name=None
    # return render_template('view_theme.html', tables = [input_data.to_html(classes = 'Userinput'), input_data_2.to_html(classes = 'Userinput')], titles = ['na', 'User Input #1', 'User Input #2'])
    
# @app.route('/table3')
# def show_table3():
    input_data_3 = pd.read_csv('static/rec/example3.csv')
    #input_data.head(1).to_html(classes = 'User Inputs')
    input_data_3.columns = ['category', 'importance', 'rating bar', 'review number', 'distance']
    input_data_3.set_index(['category'], inplace=True)
    input_data_3.index.name=None
    return render_template('view_theme.html', tables = [input_data.to_html(classes = 'Userinput'), input_data_2.to_html(classes = 'Userinput'), input_data_3.to_html(classes = 'Userinput')], titles = ['na', 'User Input #1', 'User Input #2', 'User Input #3'])

@app.route('/rec')
def Plot_rec1():
    # load data from static folder
    filename = 'static/rec/example1_densitymap.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['g_x'].values)
    coord_y = list(df['g_y'].values)
    radii = [min(0.5, x) for x in list(df['count'].values)]
    colors = ["#%02x%02x%02x" % ((0.5-r)*500, r*500, 0) for r in radii]
    
    # create a new plot with default tools, using figure
    plot1 = figure(tools=TOOLS, title='Recommendation for userinput #1 (green:high; red:low)', x_axis_label='X (km)', y_axis_label='Y (km)', x_range=(-10, 130), y_range=(-10, 90), plot_width=700, plot_height=500)
    plot1.scatter(coord_x, coord_y, legend="Recommendation", radius=0.4, fill_color=colors, fill_alpha=0.5, line_color=None)
    
    plot1.quad(top=62, bottom=52, left=5,
       right=15, legend="S Lasky Dr, Beverly Hills, CA", line_color="red", line_width=2, fill_color=None, fill_alpha=0.5)
    plot1.quad(top=15, bottom=5, left=50,
       right=60, legend="Pacific Coast Hwy, Newport Beach, CA", line_color="blue", line_width=2, fill_color=None, fill_alpha=0.5)
    plot1.quad(top=70, bottom=60, left=26,
       right=36, legend="Fair Oaks Ave, South Pasadena, CA", line_color="orange", line_width=2, fill_color=None, fill_alpha=0.5)   
    
    #script1, div = components(plot)   
    #return render_template('graph1.html', script=script, div=div)
    
#@app.route('/rec2')
#def Plot_rec2():
    # load data from static folder
    filename = 'static/rec/example2_densitymap.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['g_x'].values)
    coord_y = list(df['g_y'].values)
    radii = [min(0.5, x) for x in list(df['count'].values)]
    colors = ["#%02x%02x%02x" % ((0.5-r)*500, r*500, 0) for r in radii]
    
    # create a new plot with default tools, using figure
    plot2 = figure(tools=TOOLS, title='Recommendation for userinput #2 (green:high; red:low)', x_axis_label='X (km)', y_axis_label='Y (km)', x_range=(-10, 130), y_range=(-10, 90), plot_width=700, plot_height=500)
    plot2.scatter(coord_x, coord_y, legend="Recommendation", radius=0.4, fill_color=colors, fill_alpha=0.5, line_color=None)
    
    plot2.quad(top=52, bottom=64, left=4,
       right=16, legend="Wilshire Blvd, Los Angeles, CA", line_color="red", line_width=2, fill_color=None, fill_alpha=0.5)
    plot2.quad(top=20, bottom=12, left=60,
       right= 68, legend="Campus Dr, Irvine, CA", line_color="blue", line_width=2, fill_color=None, fill_alpha=0.5)
    plot2.quad(top=42, bottom=34, left=56,
       right=64, legend="Miller St, Anaheim, CA", line_color="orange", line_width=2, fill_color=None, fill_alpha=0.5)  
       
    #script, div = components(plot)   
    #return render_template('graph1.html', script=script, div=div)

#@app.route('/rec3')
#def Plot_rec3():
    # load data from static folder
    filename = 'static/rec/example3_densitymap.csv' 
    df = pd.DataFrame.from_csv(filename)
    coord_x = list(df['g_x'].values)
    coord_y = list(df['g_y'].values)
    radii = [min(0.5, x) for x in list(df['count'].values)]
    colors = ["#%02x%02x%02x" % ((0.5-r)*500, r*500, 0) for r in radii]
    
    # create a new plot with default tools, using figure
    plot3 = figure(tools=TOOLS, title='Recommendation for userinput #3 (green:high; red:low)', x_axis_label='X (km)', y_axis_label='Y (km)', x_range=(-10, 130), y_range=(-10, 90), plot_width=700, plot_height=500)
    plot3.scatter(coord_x, coord_y, legend="Recommendation", radius=0.4, fill_color=colors, fill_alpha=0.5, line_color=None)
    
    plot3.quad(top=65, bottom=45, left=-5,
       right=18, legend="Hollywood", line_color="red", line_width=2, fill_color=None, fill_alpha=0.5)
    plot3.quad(top=25, bottom=5, left=45,
       right=70, legend="Orange County", line_color="blue", line_width=2, fill_color=None, fill_alpha=0.5)
    plot3.quad(top=32, bottom=40, left=66,
       right=74, legend="Weir Canyon Rd, Anaheim, CA", line_color="orange", line_width=2, fill_color=None, fill_alpha=0.5) 
    
    plot = gridplot([[plot1, plot2], [plot3, None]])
    # plot = vplot(plot1, plot2, plot3)
    script, div = components(plot)   
    return render_template('graph1_theme.html', script=script, div=div)
    
@app.route('/p', methods=['GET','POST'])
def Plot_fit1():
    if request.method == 'POST':
        return redirect(url_for('prindex'))
    # load data from static folder
    filename = 'static/data_pre1.csv' 
    df = pd.DataFrame.from_csv(filename)
    rate = list(df['y_cv'].values)
    rate_pre = list(df['y_cv_pre'].values)
    num = len(rate)
    x = range(num)
    radii = 0.05
    
    # create a new plot with default tools, using figure
    plot1 = figure(tools=TOOLS, title='Predict doctor rating (mean square error: 0.77)', x_axis_label='actual rating', y_axis_label='predicted rating', x_range=(0.5, 5.5), y_range=(0, 6), plot_width=700, plot_height=500)
    plot1.scatter(rate, rate_pre, radius=radii, fill_color="green", fill_alpha=0.2, line_color=None)
    #plot.scatter(x, rate, radius=radii, fill_color="red", fill_alpha=0.2, line_color=None)
    # plot.line([1,2,3,4,5, 6], [1,2,3,4,5,6], line_width = 2)
    # plot.bar()
    
    #script, div = components(plot)   
    #return render_template('graph2.html', script=script, div=div)
    
#@app.route('/p2')
#def Plot_fit2():
    # load data from static folder
    filename = 'static/ml_fitting.csv' 
    df = pd.DataFrame.from_csv(filename)
    location = list(df['location'].values)
    score = list(df['fitscore'].values)
    radii = [x*2 for x in list(df['fitscore'].values)]
    
    # create a new plot with default tools, using figure
    plot2 = figure(tools=TOOLS, title='Predict doctor rating score', x_axis_label='Location range (km)', y_axis_label='Fitting Score', x_range=(0, 10), y_range=(0.05, 0.25), plot_width=700, plot_height=500)
    plot2.scatter(location, score, radius=radii, fill_color="red", fill_alpha=0.2, line_color=None)
    # plot.bar()
    
    plot = hplot(plot1, plot2)
    script, div = components(plot)   
    return render_template('graph2_theme.html', script=script, div=div)

# The following code deals with the interactive output with user inputs    
@app.route('/prindex',methods=['GET','POST'])
def PRindex():
    if request.method == 'GET':
        return render_template('pr_layout.html')
    else:
        # request was a POST
        # app.vars['ticker_symbol'] = request.form['ticker_info']
        #app.vars['closing_price'] = 'off'
        #app.vars['closing_price'] = request.form['close_price']
        #app.vars['adj_closing_price'] = request.form['adj_closingPrice']
        #app_lulu.vars['age'] = request.form['age_lulu']
        app.importance = request.form.getlist('importance')
        app.rating_bar = request.form.getlist('rating_bar')
        app.review_count = request.form.getlist('review_num')
        app.distance = request.form.getlist('distance')
        # write out the output
        f = open('info.txt','w')
        f.write('Importance is: %s\n'%(app.importance))
        f.write('rating_bar is: %s\n'%(app.rating_bar))
        f.write('review count is: %s\n'%(app.review_count)) 
        f.write('distance is: %s\n'%(app.distance))  
        # if bool(app.selected):
            # f.write('\n'.join(app.selected))
        f.close()
        return redirect('/prgraph')
        
@app.route('/prgraph', methods=['GET','POST'])
def Plot_prec():
    if request.method == 'POST':
        return redirect(url_for('prindex'))
    importance_arr = [float(item) for item in app.importance]
    rating_arr = [float(item) for item in app.rating_bar]
    review_arr = [float(item) for item in app.review_count]
    distance_arr = [float(item) for item in app.distance]
    category = ['Family Practice', 'Cosmetic Surgery', 'Urgent Care', 'Physical Therapy', 'Sports medicine']
    data_input = {'importance': importance_arr, 'rating bar': rating_arr, 'review number': review_arr, 'distance': distance_arr}
    df = pd.DataFrame(data_input, columns = ['importance', 'rating bar', 'review number', 'distance'],
                        index = category)
                        
    x_arr = np.arange(-10, 130)
    y_arr = 90 - np.arange(100)
    rec_map_mat = np.zeros((140, 100))
    
    cat_dict = {'Family Practice': 'static/Family Practicestats.csv', 'Cosmetic Surgery' : 'static/Cosmetic Surgeonsstats.csv',
            'Urgent Care': 'static/Urgent Carestats.csv', 'Physical Therapy': 'static/Physical Therapystats.csv',
            'Sports medicine': 'static/Sports Medicinestats.csv',
           }
    
    import_sum = float(df['importance'].sum())
    for cat in df.index:
        filename = cat_dict[cat]
        data = pd.read_csv(filename)
        rate_bar = df['rating bar'][cat]
        rev_num = df['review number'][cat]
        grid_matrix = dm.grid_mat(data, rating_bar = rate_bar, review_num = rev_num)
        f_dist = df['distance'][cat]
        density_map_mat = dm.density_map(grid_matrix, f_dist)
        dmax = density_map_mat.max()   
        den_map_nor = density_map_mat/dmax
        rec_map_mat = rec_map_mat + (df['importance'][cat]/import_sum) * den_map_nor
    g_x = np.repeat(x_arr, 100)
    g_y = np.tile(y_arr, 140)
    count = rec_map_mat.reshape(14000)
    df_output = pd.DataFrame({'g_x':g_x, 'g_y':g_y, 'count': count})
    df_nz = df_output[df_output['count'] > 0.0001]

    coord_x = list(df_nz['g_x'].values)
    coord_y = list(df_nz['g_y'].values)
    radii = [min(0.5, x) for x in list(df_nz['count'].values)]
    colors = ["#%02x%02x%02x" % ((0.5-r)*500, r*500, 0) for r in radii]
    
    plot = figure(tools=TOOLS, title='The most desirable places in Greater LA area are in green.', x_axis_label='X (km)', y_axis_label='Y (km)', x_range=(-10, 130), y_range=(-10, 90), plot_width=840, plot_height=600)
    plot.scatter(coord_x, coord_y, legend="Recommendation", radius=0.4, fill_color=colors, fill_alpha=0.5, line_color=None)
    
    plot.quad(top=65, bottom=45, left=-5,
       right=18, legend="Hollywood", line_color="red", line_width=2, fill_color=None, fill_alpha=0.5)
    plot.quad(top=25, bottom=5, left=45,
       right=70, legend="Orange County", line_color="blue", line_width=2, fill_color=None, fill_alpha=0.5)

    script, div = components(plot)   
    return render_template('graph4_theme.html', script=script, div=div)	
    
if __name__ == '__main__':
    app.debug=True
    app.run()