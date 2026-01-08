package xpath;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.StringReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.TreeMap;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.apache.commons.io.IOUtils;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

public class XpathAttrAdd {
	
	
	public static void main(String[] args){
		
		xpathPopulate();
		
		
	}
	
	
	public static void xpathPopulate(){
		
		
		URL url;
	    InputStream is = null;
	    BufferedReader br;
	    String line, content = "";

	    try {
	        url = new URL("http://google.com/");
	        is = url.openStream();  // throws an IOException
	        br = new BufferedReader(new InputStreamReader(is));

	        while ((line = br.readLine()) != null) {
	        	content += line;
	        	System.out.println(line);
	        }
	        
	        
	        
	        
	    	
	    	/*
	    	url = new URL("http://www.sensutec.com/");
	    	URLConnection con = url.openConnection();
	    	InputStream in = con.getInputStream();
	    	String encoding = con.getContentEncoding();  // ** WRONG: should use "con.getContentType()" instead but it returns something like "text/html; charset=UTF-8" so this value must be parsed to extract the actual encoding
	    	encoding = encoding == null ? "UTF-8" : encoding;
	    	content = IOUtils.toString(in, encoding);
	        */
	        
	        // Perform Task Here
	        
	       /*
	        
	        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
	        DocumentBuilder builder = factory.newDocumentBuilder();
	        InputSource isD = new InputSource(new StringReader(content));
	        Document doc = builder.parse(isD);
	        Element de = doc.getDocumentElement();
	        
	        NodeList n1 = de.getChildNodes();
	        
	        for (int i = 0; i < n1.getLength(); i++){
	        	
	        	
	        	System.out.println(n1.item(i).getNodeName());
	        	
	        	
	        }
	        
	        
	        */
	        
	        
	        Document doc = Jsoup.parse(content);
	        
	        Element html = doc.select("html").first();
	        Elements htmlChilds = html.children();
	        
	        // System.out.println(htmlChilds.size());
	        
	        ArrayList<xpath_obj> element_xpath = new ArrayList<xpath_obj>();
	        
	        element_xpath.add(new xpath_obj(html, "//html"));
	        
	        
	        element_xpath = polyElement(htmlChilds, element_xpath, "//html[1]");
	        
	        
	        for(xpath_obj xelem: element_xpath){
	        	
	        		
	        		// System.out.println(elem.tagName());
	        	
	        		
	        		System.out.println(xelem.xpath);
	        	
	        		// String tagText = elem.html();
	        		
	        		// String newTagText = tagText.substring(0, tagText.indexOf(elem.tagName()) + elem.tagName().length()) + " data-comment=\"test\" "
	        		// 		+ tagText.substring(tagText.indexOf(elem.tagName()) + elem.tagName().length());
	        		
	        		// elem.attr("name", "test");
	        		
	        	
	        		// System.out.println(elem.html());
	        		
	        		// System.out.println(newElem.html());
	        	
	        }
	        
	        
	        
	    } catch (MalformedURLException mue) {
	         mue.printStackTrace();
	    } catch (IOException ioe) {
	         ioe.printStackTrace();
	    } finally {
	        try {
	            if (is != null) is.close();
	        } catch (IOException ioe) {
	            // nothing to see here
	        }
	    }
		
		
		
		
	}
	
	
	
	public static ArrayList<xpath_obj> polyElement (Elements elemChilds, ArrayList<xpath_obj> element_xpath,
			String xpathRoot) {
		
		// ArrayList<Element> tempElementsArray = new ArrayList<Element>();
		
		TreeMap<String,Integer> tags = new TreeMap<String,Integer>();
		
		
		for(Element elem: elemChilds){
			
			if(!tags.containsKey(elem.tagName())){
				tags.put(elem.tagName(), 1);
			}else {
				tags.put(elem.tagName(), tags.get(elem.tagName())+1);
			}
			
			
			
			String xpath = xpathRoot;
			
			
			xpath += "/" + elem.tagName() + "[" + tags.get(elem.tagName()).toString() + "]";
			
			// polyElementsArray.add(elem);
			element_xpath.add(new xpath_obj(elem, xpath));
        	
    		Elements grandChildren = elem.children();
    		
    		// for(Element elem2: grandChildren)
    		// 	tempElementsArray.add(elem2);
    		
    		if(grandChildren.size() != 0){
    			element_xpath = polyElement(grandChildren, element_xpath, xpath);
    			
    		}
    		
    		
    		
    		
    	}
		
		
		
		return element_xpath;
		
		
	}
	
	
	

}
