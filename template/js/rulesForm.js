function isNumeric(input)
{
  return (input - 0) == input && input.length > 0;
}

function showHideField()
{
  var sel = document.getElementById('id_action');
  if (sel.options[sel.selectedIndex].value == 'Allow' || sel.options[sel.selectedIndex].value == 'Deny')
  {
    document.getElementById('calculation').style.display = 'none';
  }
  else
  {
    document.getElementById('calculation').style.display = '';
  }
}

function showHideForm()
{
  for(i = 0; i < 2; i++)
  {
    var type = document.getElementById ('id_form_Type_' + i);
    if(type.checked)
    {
       if(i == 0)
       {
          document.getElementById('robustForm').style.display = 'none';
          document.getElementById('simpleForm').style.display = '';
          document.getElementById('id_condition').value = '-1';
       }
       else
       {
          document.getElementById('robustForm').style.display = '';
          document.getElementById('simpleForm').style.display = 'none';
          document.getElementById('id_condition').value = '';
       }
       return;
    }
    
  }
  
  //Default to simpleForm
  document.getElementById('id_form_Type_0').checked = true; 
  document.getElementById('robustForm').style.display = 'none';
  document.getElementById('simpleForm').style.display = '';
  document.getElementById('id_condition').value = '-1';
    
}

function whichForm()
{
  //Check to see if it's a page update via the URL
  var currURL = window.location.href.split("/");
  if(isNumeric(currURL[currURL.length-1]))
  {
    document.getElementById('robustForm').style.display = '';
    document.getElementById('simpleForm').style.display = 'none';
    document.getElementById('form_Type_Q').style.display = 'none';
  }
  else
  {
    showHideForm();
  }
   
}

function startUp()
{
  showHideField();
  whichForm();
}

function condSelect(elem)
{
  var currSelID = elem.id; //$(this).attr('id');
  var thisDL = currSelID.substring(0, currSelID.lastIndexOf('_dt_CS'));
  var thisDT = thisDL + '_dt';
  var currSelVal = elem.options[elem.selectedIndex].value; //$(this).val();
  

  var nextDD = thisDL + "_dd";
  var link = "<a id=" + currSelID + '_a' + " onClick='addCondSelect(this)'>+</a>";
  
  //Remove Previous Elements
  $('#'+nextDD).remove();

  $('#' + currSelID + '_a').remove();
  //Normally have DT float
  //$('#'+thisDT).attr('style', 'float: left');

  //AND or OR
  if ((currSelVal == 0) || (currSelVal == 1))
  {
     var nextDL = nextDD + "_1_dl";
     var nextDT = nextDL + "_dt";

     //Create new dt in nextDiv and figure out how to do id's
     var addHTMLFront = "<dd id ='" + nextDD + "'>\n<dl id='" + nextDL + "'>\n<dt id='" + nextDT + "'>\n"; 
     var addHTMLBack = "\n</dt>\n</dl>\n</dd>\n";
     $("#" + thisDL).append(addHTMLFront + newCondSelect(nextDT+"_CS") + addHTMLBack);
     $('#'+thisDT).append(link);
  }
  else if (currSelVal == 2)
  {
     var currID = nextDD + '_dc';
     var label = "<label for='" + currID + "'>User/Group Name: </label>";
     var tb = "&nbsp; <input id='id_" + currID + "' maxlength=30 type='text'>";
     var addHTMLFront = "<dd id ='" + nextDD + "'>\n"; 
     var addHTMLBack = "\n</dd>\n";
     $("#" + thisDL).append(addHTMLFront + label + tb + addHTMLBack);
     $('#'+thisDT).append(link);
  }
  else if (currSelVal == 3)
  {
     var nextDL = nextDD + "_1_dl";
     var nextDT = nextDL + "_dt";
     var addHTMLFront = "<dd id ='" + nextDD + "'>\n<dl id='" + nextDL + "'>\n<dt id='" + nextDT + "' >\n"; 
     var addHTMLBack = "\n</dt>\n</dl>\n</dd>\n";
     
     $("#" + thisDL).append(addHTMLFront + newSensSelect(nextDT + '_SS') + addHTMLBack);
     $('#'+thisDT).append(link);
  }
  else if (currSelVal == 4)
  {
     var nextDL = nextDD + "_1_dl";
     var nextDT = nextDL + "_dt";
     var addHTMLFront = "<dd id ='" + nextDD + "'>\n<dl id='" + nextDL + "'>\n<dt id='" + nextDT + "' >\n"; 
     var addHTMLBack = "\n</dt>\n</dl>\n</dd>\n";
     
     $("#" + thisDL).append(addHTMLFront + newTimeSelect(nextDT + '_TM') + addHTMLBack);
     $('#'+thisDT).append(link);
  }
  else if (currSelVal == 5)
  {
     var nextDL = nextDD + "_1_dl";
     var nextDT = nextDL + "_dt";
     var addHTMLFront = "<dd id ='" + nextDD + "'>\n<dl id='" + nextDL + "'>\n<dt id='" + nextDT + "' >\n"; 
     var addHTMLBack = "\n</dt>\n</dl>\n</dd>\n";
     
     $("#" + thisDL).append(addHTMLFront + newLocationSelect(nextDT + '_LO') + addHTMLBack);
     $('#'+thisDT).append(link);
  }
  else if (currSelVal == 6)
  {
     var nextDL = nextDD + "_1_dl";
     var nextDT = nextDL + "_dt";
     var addHTMLFront = "<dd id ='" + nextDD + "'>\n<dl id='" + nextDL + "'>\n<dt id='" + nextDT + "' >\n"; 
     var addHTMLBack = "\n</dt>\n</dl>\n</dd>\n";
     
     $("#" + thisDL).append(addHTMLFront + newValueSelect(nextDT + '_VA') + addHTMLBack);
     $('#'+thisDT).append(link);
  }
}

function addCondSelect(elem)
{
  var currSelID = elem.id; 
  //Remove previous link
  $('#'+currSelID).remove();

  var prevDL = currSelID.substring(0, currSelID.lastIndexOf('_dl'));
  var prevDLRoot = prevDL.substring(0, prevDL.lastIndexOf('_'));
  
  var prevDLID = parseInt(prevDL.substring(prevDL.lastIndexOf('_'), prevDL.length));
  var extraUnder = '';
  if (isNaN(prevDLID))
  {
    extraUnder += '_'
    prevDLID = parseInt(prevDL.substring(prevDL.lastIndexOf('_')+1, prevDL.length));
  }
 
  var currDTid = prevDLID + 1
  var nextDL = prevDLRoot + extraUnder + currDTid + '_dl';

  var nextDT = nextDL + "_dt";
  
  var addHTMLFront = "<dl id='" + nextDL + "'><dt id='" + nextDT + "'>\n"; 
  var addHTMLBack = "\n</dt></dl>\n";

  //Check if the node about to be added exists
  if($('#' + nextDL).length != 0)
  {
    alert("This element has already been found, and the link to create it has beeen removed. Sorry for the inconvenience.");
    return;
  }

  if (prevDLRoot == '')
  {
    $("#simpleForm").append(addHTMLFront + newCondSelect(nextDT+"_CS") + addHTMLBack);
  }
  else
  {
    $("#" + prevDLRoot).append(addHTMLFront + newCondSelect(nextDT+"_CS") + addHTMLBack);
  }
}

function newSelect(selID, selClass, opts, otherOpts) {
   var sel = "<select id='" + selID + "' " + otherOpts + ">";
   for (i = 0; i < opts.length; i++) {
      sel += "<option value=" + opts[i][0] + ">" + opts[i][1] + "</option>";
   }
   sel += "</select>";
   return sel;
}

function newCondSelect(id) {
   var optsA = new Array('', 'AND', 'OR', 'Data Consumer', 'Sensor', 'Time', 'Location', 'Value');
   var opts = new Array();
   for( i = -1; i < optsA.length - 1; i++) {
      opts[i+1] = new Array(i, optsA[i+1]);
   }
   return newSelect(id, 'condSelect', opts, "onChange='condSelect(this)'");
}

function newSensSelect(id) {
   var optsA = new Array('', 'AND', 'OR', 'Sensor Node');
   var opts = new Array();
   for( i = -1; i < optsA.length - 1; i++) {
      opts[i+1] = new Array(i, optsA[i+1]);
   }
   return newSelect(id, '', opts, "onChange='sensSelect(this)'");
}

function newTimeSelect(id) {
   var optsA = new Array('', 'Time Zone', 'Time Range', 'Time Instants', 'Time of Day');
   var opts = new Array();
   for( i = -1; i < optsA.length - 1; i++) {
      opts[i+1] = new Array(i, optsA[i+1]);
   }
   return newSelect(id, '', opts, "onChange='timeSelect(this)'");
}

function newLocationSelect(id) {
   var optsA = new Array('', 'AND', 'OR', 'NOT', 'In', 'Place');
   var opts = new Array();
   for( i = -1; i < optsA.length - 1; i++) {
      opts[i+1] = new Array(i, optsA[i+1]);
   }
   return newSelect(id, '', opts, "onChange='locationSelect(this)'");
}

function newValueSelect(id) {
   var optsA = new Array('', 'AND', 'OR', 'NOT', 'EQ', 'LT', 'GT', 'GTEQ', 'LTEQ');
   var opts = new Array();
   for( i = -1; i < optsA.length - 1; i++) {
      opts[i+1] = new Array(i, optsA[i+1]);
   }
   return newSelect(id, '', opts, "onChange='valueSelect(this)'");
}

//TODO Use AJAX to get SN names and SC names
function sensSelect(elem) {
  var currSelID = elem.id;
  var thisDL = currSelID.substring(0, currSelID.lastIndexOf('_dt_SS'));

  var thisDT = thisDL + '_dt';
  var currSelVal = $('#' + currSelID).val();
  
  var nextDD = thisDL + "_dd";
  var nextD2 = thisDL + "_d2";
  var nextD3 = nextD2 + "_d3";
  var link = "&nbsp; <a id=" + currSelID + '_a' + " onClick='addSensSelect(this)'>+</a>";
  
  var nextDL = nextDD + "_dl";
  var nextDT = nextDL + "_dt";

  //Create new dt in nextDiv and figure out how to do id's
  var addHTMLFront = "<dd id ='" + nextDD + "'>\n<dl id='" + nextDL + "'>\n<dt id='" + nextDT + "'>\n"; 
  var addHTMLBack = "\n</dt>\n</dl>\n</dd>\n";

  //Remove Previous Elements
  $('#'+nextDD).remove();
  $('#'+currSelID+'_a').remove();
  
  if(currSelVal == 0 || currSelVal == 1)
  {
     $("#" + thisDL).append(addHTMLFront + newSensSelect(nextDT+"_SS") + addHTMLBack);
  }
  else if(currSelVal == 2)
  {
     var snID = nextD2 + "_sn";
     var sensorNode = "<br><label for='" + snID + "'>Sensor Node: </label>";
     sensorNode += "<input id='" + snID + "' maxlength=30 type='text'>";
     var scID = nextD2 + "_sc";
     var sensorChannel = "<label for='" + scID + "'>Sensor Channel: </label>";
     sensorChannel += "<input id='" + scID + "' maxlength=30 type='text'>";

     var currHTML = sensorNode + "\n<br>\n" + sensorChannel;
     
     $("#" + thisDL).append(addHTMLFront + currHTML + addHTMLBack);
     if ($("#" + nextD2).length != 0) 
     {
        $("#" + nextD2).append(link);
     }
     else
     {
        $("#" + thisDT).append(link);
     }
  }
}

function addSensSelect(elem)
{
  var currSelID = elem.id;
  var thisDL = currSelID.substring(0, currSelID.lastIndexOf('_d2_SS_a'));
  
  if(thisDL == '')
  {
    thisDL = currSelID.substring(0, currSelID.lastIndexOf('_dt_SS_a'));
  }
  var nextDL = thisDL + '_dd_dl';
  var numChild = $('#'+nextDL).children().size() + 1;

  var snID = nextDL + "_sn" + numChild;
  var sensorNode = "<label for='" + snID + "'>Sensor Node: </label>";
  sensorNode += "<input id='" + snID + "' maxlength=30 type='text'>";
  var scID = nextDL + "_sc" + numChild;
  var sensorChannel = "<label for='" + scID + "'>Sensor Channel: </label>";
  sensorChannel += "<input id='" + scID + "' maxlength=30 type='text'>";

  var currHTML = "\n<dt id='" + nextDL + numChild + "'>" + sensorNode + "\n<br>\n" + sensorChannel + "</dt>\n";
  $("#" + nextDL).append(currHTML);
}

function timeSelect(elem)
{
  var currSelID = elem.id;
  var thisDL = currSelID.substring(0, currSelID.lastIndexOf('_dt_TM'));
  var thisDT = thisDL + '_dt';
  var currSelVal = $('#' + currSelID).val();
  var currSelOpt = $('#' + currSelID + " option[value='" + currSelVal + "']").text()

  var nextDD = thisDL + '_dd';

  //Remove Child DD node
  $('#'+nextDD).remove();

  if(currSelVal == 1)
  {
     var startID = nextDD + "_ts";
     var start = "<label for='" + startID + "'>Start Range: </label>";
     start += "<input id='" + startID + "' maxlength=30 type='text'>";
     
     var endID = nextDD + "_te";
     var end = "<label for='" + endID + "'>End Range: </label>";
     end += "<input id='" + endID + "' maxlength=30 type='text'>";
     
     $('#' + thisDL).append("<dd id='" + nextDD + "'>" + start + "<br>" + end + "</dd>");
  }
  else if(currSelVal > -1)
  {
     var idLetter = currSelOpt.charAt(currSelOpt.lastIndexOf(" ") + 1);
     var timeID = nextDD + "_t" + idLetter;

     var timeItem = "<label for='" + timeID + "'>" + currSelOpt + ": </label>";
     timeItem += "<input id='" + timeID + "' maxlength=30 type='text'>";
     
     $('#' + thisDL).append("<dd id='" + nextDD + "'>" + timeItem + "</dd>");
  }
}

function locationSelect(elem)
{
  var currSelID = elem.id;
  var thisDL = currSelID.substring(0, currSelID.lastIndexOf('_dt_LO'));
  var thisDT = thisDL + '_dt';
  var currSelVal = $('#' + currSelID).val();
  var currSelOpt = $('#' + currSelID + " option[value='" + currSelVal + "']").text()

  var nextDD = thisDL + '_dd';
  var nextDL = nextDD + "_dl";
  var nextDT = nextDL + "_dt";
  
  //Create new dt in nextDiv and figure out how to do id's
  var addHTMLFront = "<dd id ='" + nextDD + "'>\n<dl id='" + nextDL + "'>\n<dt id='" + nextDT + "'>\n"; 
  var addHTMLBack = "\n</dt>\n</dl>\n</dd>\n";

  //Remove Child DD node
  $('#'+nextDD).remove();

  if(currSelVal < 3 && currSelVal > -1)
  {
     $("#" + thisDL).append(addHTMLFront + newLocationSelect(nextDT+"_LO") + addHTMLBack);
  }
  else if(currSelVal == 3)
  {
    var locXID = nextDD + "_lx";
    var locYID = nextDD + "_ly";
    var locZID = nextDD + "_lz";
    var distXID = nextDD + "_dx";
    var distYID = nextDD + "_dy";
    var distZID = nextDD + "_dz";
    
    var locXItem = "<label for='" + locXID + "'>X Coordinate:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</label>";
    locXItem += "<input id='" + locXID + "' maxlength=30 type='text'>";
    
    var distXItem = "<label for='" + distXID + "'>X Distance (in km): </label>";
    distXItem += "<input id='" + distXID + "' maxlength=30 type='text'>"; 
     
    var locYItem = "<label for='" + locYID + "'>Y Coordinate:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</label>";
    locYItem += "<input id='" + locYID + "' maxlength=30 type='text'>";
    
    var distYItem = "<label for='" + distYID + "'>Y Distance (in km): </label>";
    distYItem += "<input id='" + distYID + "' maxlength=30 type='text'>";  
     
    var locZItem = "<label for='" + locZID + "'>Z Coordinate:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</label>";
    locZItem += "<input id='" + locZID + "' maxlength=30 type='text'>";
     
    var distZItem = "<label for='" + distZID + "'>Z Distance (in km): </label>";
    distZItem += "<input id='" + distZID + "' maxlength=30 type='text'>"; 
     
    $('#' + thisDL).append("<dd id='" + nextDD + "'>" + locXItem + "<br>" + distXItem + "<br><br>" + locYItem + "<br>" + distYItem + "<br><br>" + locZItem + "<br>" + distZItem + "<br>" + "</dd>");
  }
  // TODO Make this work w/ AJAX 
  else if(currSelVal == 4)
  {
    var placeID = nextDD + "_lp";
    
    var placeItem = "<label for='" + placeID + "'>Place: </label>";
    placeItem += "<input id='" + placeID + "' maxlength=30 type='text'>"; 
  
    $('#' + thisDL).append("<dd id='" + nextDD + "'>" + placeItem + "</dd>");
  }
}

function valueSelect(elem)
{
  var currSelID = elem.id;
  var thisDL = currSelID.substring(0, currSelID.lastIndexOf('_dt_VA'));
  var thisDT = thisDL + '_dt';
  var currSelVal = $('#' + currSelID).val();
  var currSelOpt = $('#' + currSelID + " option[value='" + currSelVal + "']").text()

  var nextDD = thisDL + '_dd';
  var nextDL = nextDD + "_dl";
  var nextDT = nextDL + "_dt";
  
  //Create new dt in nextDiv and figure out how to do id's
  var addHTMLFront = "<dd id ='" + nextDD + "'>\n<dl id='" + nextDL + "'>\n<dt id='" + nextDT + "'>\n"; 
  var addHTMLBack = "\n</dt>\n</dl>\n</dd>\n";

  //Remove Child DD node
  $('#'+nextDD).remove();

  if(currSelVal > -1 && currSelVal < 3)
  {
     $("#" + thisDL).append(addHTMLFront + newValueSelect(nextDT+"_VA") + addHTMLBack);
  }
  else if(currSelVal > -1)
  {
     var valueID = nextDD + "_vt";

     var valueItem = "<label for='" + valueID + "'>Value: </label>";
     valueItem += "<input id='" + valueID + "' maxlength=30 type='text'>";
     
     $('#' + thisDL).append("<dd id='" + nextDD + "'>" + valueItem + "</dd>");
  }
}

$(document).ready(function() {
   startUp();
});
