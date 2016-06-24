# Python module to use when working with the tulip module in a Jupyter / IPython notebook
# It enables to inline Tulip WebGL graph visualizations in the notebook

# That code is freely inspired from the great mpld3 project
# (see https://github.com/mpld3/mpld3/tree/master/mpld3)

import base64
import jinja2
import random
import os.path
import tempfile
import shutil
from tulip import *

TULIPJS_HTML = jinja2.Template("""
<style type="text/css">div.output_area .tulip_viz { max-width:100%; height:300; }</style>
<div id="{{ vizid }}" class="tulip_viz"></div>
<script type="text/javascript">
  require.config({paths: {tulip: "{{ tulipjs_url[:-3] }}",
                          base64utils: "{{ base64utils_url[:-3] }}"}});
  require(["tulip", "base64utils"], function(tulip, base64utils) {

    function initTulipGraphVisualization() {
      if (!tulip.isLoaded()) {
        setTimeout(initTulipGraphVisualization, 1000);
      } else {
        console.log("OK");
        var tlpbgzGraphBase64 = "{{ tlpbgz_graph_base64 }}";
        var tlpbgzGraphBinary = base64utils.base64DecToArr(tlpbgzGraphBase64);
        var container = document.getElementById("{{ vizid }}");
        var tulipView = tulip.View(container, 400, 300);
        tulipView.loadGraphFromData("graph.tlpb.gz", tlpbgzGraphBinary);
        tulipView.centerScene();
        tulipView.draw();
      }
    };

    initTulipGraphVisualization();

  });
</script>
""")

def copyNeededFilesToWebServer():

    nbextension = True
    try:
        from IPython.html import install_nbextension
    except ImportError:
        nbextension = False

    moduleDir = os.path.dirname(os.path.abspath(__file__))

    tulipjs_file = os.path.join(moduleDir, 'js/tulip.js')
    tulipjsmem_file = os.path.join(moduleDir, 'js/tulip.js.mem')
    tulipjsdata_file = os.path.join(moduleDir, 'js/tulip.data')
    base64utils_file = os.path.join(moduleDir, 'js/base64utils.js')

    required_files = [tulipjs_file, tulipjsmem_file, tulipjsdata_file, base64utils_file]

    tulipjs = os.path.basename(tulipjs_file)
    base64utilsjs = os.path.basename(base64utils_file)

    if nbextension:

        prefix = '/nbextensions/'

        def _install_nbextension(extensions):
            """Wrapper for IPython.html.install_nbextension."""
            import IPython
            if IPython.version_info[0] >= 3:
                for extension in extensions:
                    install_nbextension(extension, user=True)
            else:
                install_nbextension(extensions)

        try:
            _install_nbextension(required_files)
        except IOError:
            # files may be read only. We'll try deleting them and re-installing
            from IPython.utils.path import get_ipython_dir
            nbext = os.path.join(get_ipython_dir(), "nbextensions")

            for req_file in required_files:
                dest = os.path.join(nbext, os.path.basename(req_file))
                if os.path.exists(dest):
                    os.remove(dest)
            _install_nbextension(required_files)


    return prefix + tulipjs, prefix + base64utilsjs

def getGraphVisualizationHTML(graph):
    vizid = 'fig_el' + str(int(random.random() * 1E10))
    tulipjs_url, base64utilsjs_url = copyNeededFilesToWebServer()
    dirpath = tempfile.mkdtemp()
    tmpGraphFile = os.path.join(dirpath, 'graph.tlpb.gz')
    tlp.saveGraph(graph, tmpGraphFile)
    tlpbgzGraphData = open(tmpGraphFile, 'rb').read()
    tlpbgzGraphDataBase64 = base64.b64encode(tlpbgzGraphData)
    shutil.rmtree(dirpath)
    return TULIPJS_HTML.render(vizid=vizid,
                               tulipjs_url=tulipjs_url,
                               base64utils_url=base64utilsjs_url,
                               tlpbgz_graph_base64=tlpbgzGraphDataBase64)

def display(graph):
    from IPython.display import HTML
    return HTML(getGraphVisualizationHTML(graph))
