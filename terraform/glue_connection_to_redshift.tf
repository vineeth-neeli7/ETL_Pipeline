resource "aws_glue_connection" "redshift_connection_team2" {
  name = "redshift_connection_team2"

  connection_properties = {
    "JDBC_CONNECTION_URL" = "jdbc:redshift://${aws_redshift_cluster.redshift_team2.endpoint}/sales_data_redshift_team2"
    "USERNAME"            = "adminuser"
    "PASSWORD"            = "Adminuser123"
  }

  physical_connection_requirements {
    availability_zone        = "us-east-2a" 
    subnet_id                = "subnet-0eb61b98a8ca52777"
    security_group_id_list   = [aws_security_group.redshift_sg_team2.id]
  }

  depends_on = [aws_redshift_cluster.redshift_team2]
}
