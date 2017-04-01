package com.ahalogy.wikipedia;

import com.mysql.cj.jdbc.MysqlDataSource;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.common.SolrInputDocument;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

public class WikipediaDbToSolr {
    public static void main(String[] args) throws Exception {
        MysqlDataSource dataSource = new MysqlDataSource();
        dataSource.setUser("ahalogy");
        dataSource.setPassword("ahalogy");
//        dataSource.setServerName("localhost");
//        dataSource.setDatabaseName("wikipedia");
        dataSource.setUrl("jdbc:mysql://localhost/wikipedia?useUnicode=true&useJDBCCompliantTimezoneShift=true&useLegacyDatetimeCode=false&serverTimezone=UTC&useSSL=false&maxAllowedPacket=10485760");

        final String solrUrl = "http://localhost:8983/solr/wikipedia_core";
        final HttpSolrClient solrClient = new HttpSolrClient.Builder(solrUrl).build();

        int dbBatchSize = 10000;
        int solrBatchSize = 1000;
        int offset = 0;

        try (
                final Connection con = dataSource.getConnection();
                final Statement stmt = con.createStatement()
        ) {
            while (doBatch(stmt, solrClient, dbBatchSize, offset, solrBatchSize)) {
                offset += dbBatchSize;
            }
        }
    }

    private static boolean doBatch(
            Statement stmt, HttpSolrClient solrClient,
            int dbBatchSize, int offset, int solrBatchSize
    ) throws Exception {
        System.out.println(String.format("fetching from mysql with offset %d...", offset));
        final String sql = String.format("select * from page limit %d offset %d", dbBatchSize, offset);
        int counter = 0;
        final List<SolrInputDocument> solrDocs = new ArrayList<>();
        try (
                final ResultSet rs = stmt.executeQuery(sql)
        ) {
            while (rs.next()) {
                counter++;
                final int id = rs.getInt("id");
//                final String name = rs.getString("name").replaceAll("\"", "\\\\\"");
//                final String text = rs.getString("text").replaceAll("\"", "\\\\\"").replaceAll("\n", " ");
                final String name = rs.getString("name");
                final String text = rs.getString("text");
                final int isDisambiguation = rs.getBoolean("isDisambiguation") ? 1 : 0;
//                final String s = String.format("{\"id\":\"%s\", \"page_name\":\"%s\", \"page_text\":\"%s\", \"is_disambiguation\":%d}",
//                        id, name, text, isDisambiguation);
//                out.println(s);
//                    if (counter >= 0) break;

                final SolrInputDocument doc = new SolrInputDocument();
                doc.addField("id", id);
                doc.addField("page_name", name);
                doc.addField("page_text", text);
                doc.addField("is_disambiguation", isDisambiguation);
                solrDocs.add(doc);

                if (counter % solrBatchSize == 0) {
                    System.out.println(String.format("writing %d to solr...", solrDocs.size()));
                    solrClient.add(solrDocs);
                    solrClient.commit();
                    solrDocs.clear();
                }
            }
        }

        if (solrDocs.size() > 0) {
            System.out.println("writing to solr...");
            solrClient.add(solrDocs);
            solrClient.commit();
        }

        return (counter == dbBatchSize);
    }
}
