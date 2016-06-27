# Python module to use when working with the tulip module in a Jupyter / IPython notebook
# It enables to inline Tulip WebGL graph visualizations in the notebook

# That code is freely inspired from the great mpld3 project
# (see https://github.com/mpld3/mpld3/tree/master/mpld3)

import sys
import base64
import jinja2
import random
import os.path
import tempfile
import shutil
import IPython
from IPython.core.getipython import get_ipython
from IPython.core.display import display as ipythondisplay
from tulip import *

TULIPJS_HTML = jinja2.Template("""
<style type="text/css">
.tulip_viz {
  height: 400px;
  border: 1px solid black;
}
.interactor_button {
  position: absolute;
  left: 5px !important;
  z-index: 10;
}
.center_button {
  position: absolute;
  right: 0px !important;
  top: 0px !important;
  z-index: 10;
}
.fullscreen_button {
  position: absolute;
  right: 0px !important;
  top: 45px !important;
  z-index: 10;
}
</style>

<link rel="stylesheet" href=""/>

<div id="toolbar-options{{ vizid }}" class="hidden">
   <a class="interactor-znp" href="#"><i class="fa fa-hand-paper-o" aria-hidden="true"></i></a>
   <a class="interactor-zoom" href="#"><i class="fa fa-search-plus"></i></a>
   <a class="interactor-fisheye" href="#"><i class="fa fa-eye"></i></a>
</div>

<div id="{{ vizid }}" class="tulip_viz">

<div id="toolbar{{ vizid }}" class="btn-toolbar btn-toolbar-dark interactor_button hidden">
    <i class="fa fa-hand-paper-o" aria-hidden="true"></i>
</div>

<div id="center{{ vizid }}" class="btn-toolbar btn-toolbar-dark center_button hidden">
    <i class="fa fa-arrows" aria-hidden="true"></i>
</div>

<div id="fullscreen{{ vizid }}" class="btn-toolbar btn-toolbar-dark fullscreen_button hidden">
    <i class="fa fa-arrows-alt" aria-hidden="true"></i>
</div>

</div>

<script type="text/javascript">

  var hostname = window.location.hostname;

  // case where we are running a local notebook server, load required assets from it
  if (hostname == "localhost" || hostname == "127.0.0.1") {
    require.config({paths: {tulip: "{{ tulipjs_url[:-3] }}",
                            base64utils: "{{ base64utils_url[:-3] }}",
                            jquerytoolbar: "{{ jquerytoolbarjs_url[:-3] }}"}});

    if ($("#jqtoolbarcss").length == 0) {
      $("head").append('<link id="jqtoolbarcss" rel="stylesheet" href="{{ jquerytoolbarcss_url }}" type="text/css" />');
    }

    if ($("#fontawesomecss").length == 0) {
      $("head").append('<link id="fontawesomecss" rel="stylesheet" href="{{ fontawesomecss_url }}" type="text/css" />');
    }

  // otherwise, we assume that we are only rendering a static html notebook through nbviewer
  // so load required assets from rawgit (GitHub CDN)
  } else {
    require.config({paths: {tulip: "https://rawgit.com/anlambert/tulip_python_notebook/master/tulipnb/tulipjs/tulip",
                            base64utils: "https://rawgit.com/anlambert/tulip_python_notebook/master/tulipnb/tulipjs/base64utils",
                            jquerytoolbar: "https://rawgit.com/anlambert/tulip_python_notebook/master/tulipnb/tulipjs/jquery.toolbar.min"}});

    if ($("#jqtoolbarcss").length == 0) {
      $("head").append('<link id="jqtoolbarcss" rel="stylesheet" href="https://rawgit.com/anlambert/tulip_python_notebook/master/tulipnb/tulipjs/jquery.toolbar.css" type="text/css" />');
    }

    if ($("#fontawesomecss").length == 0) {
      $("head").append('<link id="fontawesomecss" rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css" type="text/css" />');
    }

    window.tulipConf = {
      modulePrefixURL: "https://rawgit.com/anlambert/tulip_python_notebook/master/tulipnb/tulipjs/",
      filePackagePrefixURL: "https://rawgit.com/anlambert/tulip_python_notebook/master/tulipnb/tulipjs/",
      memoryInitializerPrefixURL: "https://rawgit.com/anlambert/tulip_python_notebook/master/tulipnb/tulipjs/"
    };

  }

  require(["tulip", "base64utils", "jquerytoolbar"], function(tulip, base64utils) {

    var tulipView;

    function initTulipGraphVisualization() {
      if (!tulip.isLoaded()) {
        setTimeout(initTulipGraphVisualization, 1000);
      } else {
        var tlpbgzGraphBase64 = "{{ tlpbgz_graph_base64 }}";
        var tlpbgzGraphBinary = base64utils.base64DecToArr(tlpbgzGraphBase64);
        var container = document.getElementById("{{ vizid }}");
        tulipView = tulip.View(container);
        $("#toolbar{{ vizid }}").removeClass('hidden');
        $("#center{{ vizid }}").removeClass('hidden');
        $("#fullscreen{{ vizid }}").removeClass('hidden');
        tulipView.loadGraphFromData("graph.tlpb.gz", tlpbgzGraphBinary);
        tulipView.centerScene();
        tulipView.draw();
      }
    };

    $("#toolbar-options{{ vizid }}").find(".interactor-znp").on('click', function() {
      tulipView.activateInteractor('ZoomAndPan');
    });

    $("#toolbar-options{{ vizid }}").find(".interactor-zoom").on('click', function() {
      tulipView.activateInteractor('RectangleZoom');
    });

    $("#center{{ vizid }}").on('click', function() {
      tulipView.centerScene();
    });

    $("#fullscreen{{ vizid }}").on('click', function() {
      tulipView.fullScreen();
    });

    $("#toolbar-options{{ vizid }}").find(".interactor-fisheye").on('click', function() {
      tulipView.activateInteractor('Fisheye');
    });

    $("#toolbar-options{{ vizid }}").find('a').on('click', function() {
      $this = $(this);
      $button = $('#toolbar{{ vizid }}');
      $newClass = $this.find('i').attr('class').substring(3);
      $oldClass = $button.find('i').attr('class').substring(3);
      if($newClass != $oldClass) {
        $button.find('i').animate({
          top: "+=50",
          opacity: 0
        }, 200, function() {
          $(this).removeClass($oldClass).addClass($newClass).css({top: "-=100", opacity: 1}).animate({
            top: "+=50"
          });
        });
      }
    });

    $('#toolbar{{ vizid }}').toolbar({
      content: '#toolbar-options{{ vizid }}',
      position: 'bottom',
      style: 'dark',
      event: 'click',
      hideOnClick: true
    });

    initTulipGraphVisualization();

  });
</script>
""")

def copyNeededFilesToWebServer():

    nbextension = True
    try:
        if IPython.version_info[0] >= 4:
            from notebook import install_nbextension
        else:
            from IPython.html import install_nbextension
    except ImportError:
        nbextension = False

    moduleDir = os.path.dirname(os.path.abspath(__file__))

    tulipjs_files = os.path.join(moduleDir, 'tulipjs')

    required_files = [tulipjs_files]

    if nbextension:

        def _install_nbextension(extensions):
            """Wrapper for IPython.html.install_nbextension."""
            if IPython.version_info[0] >= 3:
                for extension in extensions:
                    install_nbextension(extension, user=True, verbose=0)
            else:
                install_nbextension(extensions, verbose=0)

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

    prefix = '/nbextensions/tulipjs/'
    urls = {}
    urls['tulipjs'] = prefix + 'tulip.js'
    urls['base64utilsjs'] = prefix + 'base64utils.js'
    urls['jquerytoolbarjs'] = prefix + 'jquery.toolbar.min.js'
    urls['jquerytoolbarcss'] = prefix + 'css/jquery.toolbar.css'
    urls['fontawesomecss'] = prefix + 'css/font-awesome.min.css'

    return urls

def getGraphVisualizationHTML(graph):
    vizid = 'fig_el' + str(int(random.random() * 1E10))
    urls = copyNeededFilesToWebServer()
    dirpath = tempfile.mkdtemp()
    tmpGraphFile = os.path.join(dirpath, 'graph.tlpb.gz')
    tlp.saveGraph(graph, tmpGraphFile)
    tlpbgzGraphData = open(tmpGraphFile, 'rb').read()
    if sys.version_info[0] == 3:
        tlpbgzGraphDataBase64 = str(base64.b64encode(tlpbgzGraphData), 'utf-8')
    else:
        tlpbgzGraphDataBase64 = base64.b64encode(tlpbgzGraphData)
    shutil.rmtree(dirpath)
    return TULIPJS_HTML.render(vizid=vizid,
                               tulipjs_url=urls['tulipjs'],
                               base64utils_url=urls['base64utilsjs'],
                               jquerytoolbarjs_url=urls['jquerytoolbarjs'],
                               jquerytoolbarcss_url=urls['jquerytoolbarcss'],
                               fontawesomecss_url=urls['fontawesomecss'],
                               tlpbgz_graph_base64=tlpbgzGraphDataBase64)

def display(graph):
    ipythondisplay(graph)

ip = get_ipython()
formatter = ip.display_formatter.formatters['text/html']
formatter.for_type(tlp.Graph, lambda graph: getGraphVisualizationHTML(graph))
