using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;

namespace BotanicalBadAssPatcher
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            OpenFileDialog d = new OpenFileDialog();
            d.ShowDialog(this);
            textBox1.Text = d.FileName;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string filename = textBox1.Text;
            FileStream f;
            try
            {
                f = File.Open(filename, FileMode.Open, FileAccess.ReadWrite);
            }
            catch
            {
                label4.Text = "Error opening file";
                label4.ForeColor = Color.Red;
                return;
            }
            label4.Text = "Searching for bug...";
            label4.ForeColor = Color.Black;
            long len = f.Length;
            int l = (int)len;
            if (l < len) {
                label4.Text = "File too large";
                label4.ForeColor = Color.Red;
                f.Close();
                return;
            }
            byte[] buf = new byte[f.Length];
            f.Read(buf, 0, l);
            string search = "journal_allnotes";
            for (int i = 0; i < buf.Length; i++) {
                string s;
                try
                {
                    s = Encoding.ASCII.GetString(buf, i, search.Length);
                }
                catch
                {
                    label4.Text = "Unable to locate journal_allnotes :(";
                    label4.ForeColor = Color.Red;
                    f.Close();
                    return;
                }

                if (s == search)
                {
                    s = Encoding.ASCII.GetString(buf, i - 8, 8);
                    if (s.CompareTo("plants") == 0)
                    {
                        label4.Text = "The game has already been fixed";
                        label4.ForeColor = Color.Green;
                        f.Close();
                        return;
                    }
                    if (s.CompareTo("plant") != 0)
                    {
                        label4.Text = "Unable to locate bugged string :( " + s.CompareTo("plant");
                        label4.ForeColor = Color.Red;
                        f.Close();
                        return;
                    }
                    f.Seek(i-8, SeekOrigin.Begin);
                    byte[] patch = Encoding.ASCII.GetBytes("plants\0\0");
                    f.Write(patch, 0, 8);
                    f.Close();
                    label4.Text = "Patch successful!";
                    label4.ForeColor = Color.Green;
                    return;
                }
            }
        }
    }
}
