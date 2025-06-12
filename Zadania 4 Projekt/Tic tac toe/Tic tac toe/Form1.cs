using System;
using System.Windows.Forms;

namespace Tic_tac_toe
{
    public partial class Form1 : Form
    {
        private char currentPlayer = 'X';
        private Button[] boardButtons;

        public Form1()
        {
            InitializeComponent();
            this.Load += Form1_Load;
        }

        private void Form1_Load(object? sender, EventArgs e)
        {
            // Przypisz przyciski do tablicy
            boardButtons = new Button[]
            {
                button1, button2, button3,
                button4, button5, button6,
                button7, button8, button9
            };

            // Pod³¹cz jedno wspólne zdarzenie klikniêcia
            foreach (var btn in boardButtons)
            {
                btn.Click += Button_Click;
                btn.Text = "";
            }
        }

        private void Button_Click(object sender, EventArgs e)
        {
            Button clickedButton = (Button)sender;

            if (clickedButton.Text == "")
            {
                clickedButton.Text = currentPlayer.ToString();
                clickedButton.Enabled = false;

                if (CheckWin())
                {
                    MessageBox.Show($"Gracz {currentPlayer} wygra³!", "Koniec gry");
                    ResetGame();
                }
                else if (IsDraw())
                {
                    MessageBox.Show("Remis!", "Koniec gry");
                    ResetGame();
                }
                else
                {
                    currentPlayer = (currentPlayer == 'X') ? 'O' : 'X';
                }
            }
        }

        private bool CheckWin()
        {
            int[,] winningCombos = {
                {0,1,2}, {3,4,5}, {6,7,8}, // wiersze
                {0,3,6}, {1,4,7}, {2,5,8}, // kolumny
                {0,4,8}, {2,4,6}           // przek¹tne
            };

            for (int i = 0; i < winningCombos.GetLength(0); i++)
            {
                int a = winningCombos[i, 0];
                int b = winningCombos[i, 1];
                int c = winningCombos[i, 2];

                Console.WriteLine($"{a},{b},{c} -> {boardButtons[a].Text}, {boardButtons[b].Text}, {boardButtons[c].Text}");
                if (boardButtons[a].Text == currentPlayer.ToString() &&
                    boardButtons[b].Text == currentPlayer.ToString() &&
                    boardButtons[c].Text == currentPlayer.ToString())
                {
                    HighlightWinningButtons(a, b, c);
                    return true;
                }

            }

            return false;
        }

        private bool IsDraw()
        {
            foreach (var btn in boardButtons)
            {
                if (btn.Text == "")
                    return false;
            }
            return true;
        }

        private void ResetGame()
        {
            foreach (var btn in boardButtons)
            {
                btn.Text = "";
                btn.Enabled = true;
                btn.BackColor = SystemColors.Control;
            }

            currentPlayer = 'X';
        }
        private void HighlightWinningButtons(int a, int b, int c)
        {
            boardButtons[a].BackColor = Color.LightGreen;
            boardButtons[b].BackColor = Color.LightGreen;
            boardButtons[c].BackColor = Color.LightGreen;
        }
    }
}
