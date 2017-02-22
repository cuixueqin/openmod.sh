import flask
import json
from plotly.utils import PlotlyJSONEncoder

from openmod.sh.web import app

from openmod.sh.visualization import (make_regionplot_dict,
                                      make_timeseriesplot_dict)
from openmod.sh.api import (provide_element_api, json_to_db, 
                           provide_elements_api, provide_sequence_api, 
                           allowed_file, explicate_hubs)
from openmod.sh.forms import ComputeForm


@app.route('/API/element', methods=['GET', 'POST'])
def provide_element_api_route():
    if flask.request.method == 'GET':
        query_args = flask.request.args.to_dict()
        if 'id' in query_args.keys():
            json = provide_element_api(query_args)
            return flask.jsonify(json)
        return "Please provide correct query parameters. At least 'id'."
    if flask.request.method == 'POST':
        data = flask.request.get_json()
        json_to_db(data)
        return flask.render_template('imported_successfully.html')

@app.route('/API/elements', methods=['GET'])
def provide_elements_api_route():
    query_args = flask.request.args.to_dict()
    json = provide_elements_api(query_args)
    return flask.jsonify(json)

@app.route('/API/sequence', methods=['GET'])
def provide_sequence_api_route():
    query_args = flask.request.args.to_dict()
    if 'id' in query_args.keys():
        json = provide_sequence_api(query_args)
        return flask.jsonify(json)
    return "Provide at least id as query parameter."

@app.route('/import', methods=['GET', 'POST'])
def upload_file():
    if flask.request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in flask.request.files:
            flask.flash('No file part')
            return flask.redirect(flask.request.url)
        file = flask.request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flask.flash('No selected file')
            return flask.redirect(flask.request.url)
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            json_file = json.loads(str(file.read(), 'utf-8'))
            if json_file['api_parameters']['query']['hubs_explicitly'] == 'false':
                json_file = explicate_hubs(json_file)
            json_to_db(json_file)

            return flask.render_template('imported_successfully.html')
    return flask.render_template('import.html')


@app.route('/export')
def export_dataset():
    return flask.render_template('export.html')

@app.route('/id_editor')
def id_editor():
    return flask.redirect('/static/iD/index.html')

@app.route('/edit_scenario', methods=['GET', 'POST'])
def edit_scenario():
    query_args = flask.request.args.to_dict()
    query_args['expand'] = 'children'
    scenario = provide_element_api(query_args)
    
    graph = make_regionplot_dict(scenario)
    region_plot_id = "Region Plot"
    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    region_plot_json = json.dumps(graph, cls=PlotlyJSONEncoder)
    
    graph = make_timeseriesplot_dict(scenario)
    timeseries_plot_id = "Timeseries Plot"
    timeseries_plot_json = json.dumps(graph, cls=PlotlyJSONEncoder)

    return flask.render_template('edit_scenario.html', scenario=scenario,
                                 region_plot_id=region_plot_id,
                                 region_plot_json=region_plot_json,
                                 timeseries_plot_id=timeseries_plot_id,
                                 timeseries_plot_json=timeseries_plot_json)

@app.route('/scenario_overview')
def show_scenarios():
    model='pypsa'


    scenarios = provide_elements_api({'type': 'scenario',
                                      'parents': 'false',
                                      'predecessors': 'false',
                                      'successors': 'false',
                                      'sequences': 'false',
                                      'geom': 'false'})
    scenarios.pop('api_parameters')

    for k,v in scenarios.items():
        # additional information for scenario overview
        scenarios[k]['json'] = "/API/element?id="+str(k)+"&expand=children"

    return flask.render_template('show_scenarios.html',
                                 scenarios=scenarios,
                                 model=model)

@app.route('/compute_results', methods=['GET', 'POST'])
def compute_results(model='oemof'):
    # model will come l
    scenario = flask.request.args.get('scenario', '')
    form = ComputeForm()
    if form.validate_on_submit():
        scn_name = form.scn_name.data
        return flask.redirect(flask.url_for('/show_results'))

    if model == 'oemof':
        return flask.render_template('compute_results.html',
                                     model=model,
                                     form=form,
                                     scenario_default=scenario)
@app.route('/show_results', methods=['GET', 'POST'])
def show_results():
    flask.flash('Processing results...')
    return flask.render_template('show_results.html')


@app.route('/main_menu')
def main_menu():
    return flask.render_template('main_menu.html')

##### Persistence code ends here ##############################################


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)